from typing import Protocol

from sandpiper.recipe.domain.recipe import InsertedRecipe, Recipe


class RecipeRepository(Protocol):
    def save(self, recipe: Recipe, ingredient_page_ids: list[str]) -> InsertedRecipe: ...
