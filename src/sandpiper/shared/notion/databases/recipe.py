from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Relation, Title, Url  # type: ignore[import-untyped]

DATABASE_ID = "64b6d5f1254741a2a74d25f0c4df041e"


@notion_prop("名前")
class RecipeName(Title):  # type: ignore[misc]
    ...


@notion_prop("食材")
class RecipeIngredientsProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("Reference")
class RecipeReferenceProp(Url):  # type: ignore[misc]
    ...
