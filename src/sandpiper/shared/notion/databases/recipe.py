from lotion import notion_prop
from lotion.properties import Relation, Title, Url

DATABASE_ID = "64b6d5f1254741a2a74d25f0c4df041e"


@notion_prop("名前")
class RecipeName(Title): ...


@notion_prop("食材")
class RecipeIngredientsProp(Relation): ...


@notion_prop("Reference")
class RecipeReferenceProp(Url): ...
