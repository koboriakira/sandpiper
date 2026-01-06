import os

from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]
from notion_client import Client

from sandpiper.recipe.domain.recipe import Ingredient, InsertedRecipe, Recipe
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import RecipeIngredientsProp, RecipeName


@notion_database(DatabaseId.RECIPE)
class RecipePage(BasePage):  # type: ignore[misc]
    name: RecipeName
    ingredients: RecipeIngredientsProp | None = None

    @staticmethod
    def generate(recipe: Recipe, ingredient_page_ids: list[str]) -> "RecipePage":
        properties = [
            RecipeName.from_plain_text(recipe.title),
        ]
        if ingredient_page_ids:
            properties.append(RecipeIngredientsProp.from_id_list(ingredient_page_ids))
        return RecipePage.create(properties=properties)  # type: ignore[no-any-return]


class NotionRecipeRepository:
    def __init__(self) -> None:
        self.lotion_client = Lotion.get_instance()
        self.notion_client = Client(auth=os.environ.get("NOTION_TOKEN"))

    def save(self, recipe: Recipe, ingredient_page_ids: list[str]) -> InsertedRecipe:
        recipe_page = RecipePage.generate(recipe, ingredient_page_ids)
        page = self.lotion_client.create_page(recipe_page)
        page_id = page.id

        self._update_reference_url(page_id, recipe.reference_url)
        self._append_recipe_content_blocks(page_id, recipe.ingredients, recipe.steps)

        return InsertedRecipe(
            id=page_id,
            title=recipe.title,
        )

    def _update_reference_url(self, page_id: str, reference_url: str | None) -> None:
        """ReferenceプロパティにURLを設定する"""
        if not reference_url:
            return

        self.notion_client.pages.update(
            page_id=page_id,
            properties={
                "Reference": {
                    "url": reference_url,
                }
            },
        )

    def _append_recipe_content_blocks(
        self,
        page_id: str,
        ingredients: list[Ingredient],
        steps: list[str],
    ) -> None:
        """レシピのページ本文に材料と工程を追加する"""
        blocks: list[dict[str, object]] = []

        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "材料"}}]},
            }
        )

        for ingredient in ingredients:
            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"{ingredient.name}: {ingredient.quantity}"},
                            }
                        ]
                    },
                }
            )

        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "工程"}}]},
            }
        )

        for step in steps:
            blocks.append(
                {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": step},
                            }
                        ]
                    },
                }
            )

        self.notion_client.blocks.children.append(
            block_id=page_id,
            children=blocks,
        )
