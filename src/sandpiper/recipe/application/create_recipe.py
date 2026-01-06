from dataclasses import dataclass

from sandpiper.recipe.domain.recipe import Ingredient, InsertedRecipe, Recipe
from sandpiper.recipe.domain.recipe_repository import RecipeRepository
from sandpiper.recipe.domain.shopping_repository import ShoppingRepository


@dataclass
class IngredientRequest:
    name: str
    quantity: str


@dataclass
class CreateRecipeRequest:
    title: str
    reference_url: str | None
    ingredients: list[IngredientRequest]
    steps: list[str]


@dataclass
class CreateRecipe:
    _recipe_repository: RecipeRepository
    _shopping_repository: ShoppingRepository

    def __init__(
        self,
        recipe_repository: RecipeRepository,
        shopping_repository: ShoppingRepository,
    ) -> None:
        self._recipe_repository = recipe_repository
        self._shopping_repository = shopping_repository

    def execute(self, request: CreateRecipeRequest) -> InsertedRecipe:
        ingredient_page_ids: list[str] = []
        ingredients: list[Ingredient] = []

        for ingredient_request in request.ingredients:
            page_id = self._shopping_repository.find_or_create(ingredient_request.name)
            ingredient_page_ids.append(page_id)
            ingredients.append(
                Ingredient(
                    name=ingredient_request.name,
                    quantity=ingredient_request.quantity,
                )
            )

        recipe = Recipe(
            title=request.title,
            reference_url=request.reference_url,
            ingredients=ingredients,
            steps=request.steps,
        )

        inserted_recipe = self._recipe_repository.save(recipe, ingredient_page_ids)
        print(f"Created Recipe: {inserted_recipe}")
        return inserted_recipe
