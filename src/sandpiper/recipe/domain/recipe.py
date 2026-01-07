from dataclasses import dataclass


@dataclass
class Ingredient:
    """食材を表すドメインモデル"""

    name: str
    quantity: str


@dataclass
class Recipe:
    """レシピを表すドメインモデル"""

    title: str
    reference_url: str | None
    ingredients: list[Ingredient]
    steps: list[str]


@dataclass
class InsertedRecipe:
    """作成されたレシピを表すドメインモデル"""

    id: str
    title: str
