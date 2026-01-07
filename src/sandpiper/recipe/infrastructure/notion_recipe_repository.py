from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]
from lotion.block import BulletedListItem, Heading  # type: ignore[import-untyped]

from sandpiper.recipe.domain.recipe import InsertedRecipe, Recipe
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import RecipeIngredientsProp, RecipeName, RecipeReferenceProp


@notion_database(DatabaseId.RECIPE)
class RecipePage(BasePage):  # type: ignore[misc]
    name: RecipeName
    ingredients: RecipeIngredientsProp | None = None

    @staticmethod
    def generate(recipe: Recipe, ingredient_page_ids: list[str]) -> "RecipePage":
        properties = [
            RecipeName.from_plain_text(recipe.title),
        ]
        if recipe.reference_url:
            properties.append(RecipeReferenceProp.from_url(recipe.reference_url))
        if ingredient_page_ids:
            properties.append(RecipeIngredientsProp.from_id_list(ingredient_page_ids))
        blocks = []
        blocks.append(Heading.from_plain_text(heading_size=2, text="食材"))
        for ingredient in recipe.ingredients:
            blocks.append(BulletedListItem.from_plain_text(f"{ingredient.name}: {ingredient.quantity}"))
        blocks.append(Heading.from_plain_text(heading_size=2, text="工程"))
        for step in recipe.steps:
            blocks.append(BulletedListItem.from_plain_text(step))
        return RecipePage.create(properties=properties, blocks=blocks)  # type: ignore[no-any-return]


class NotionRecipeRepository:
    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def save(self, recipe: Recipe, ingredient_page_ids: list[str]) -> InsertedRecipe:
        recipe_page = RecipePage.generate(recipe, ingredient_page_ids)
        page = self._client.create_page(recipe_page)
        return InsertedRecipe(
            id=page.id,
            title=recipe.title,
        )
