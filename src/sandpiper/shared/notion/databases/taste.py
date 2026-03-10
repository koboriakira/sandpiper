from lotion import notion_prop
from lotion.properties import MultiSelect, Relation, Select, Text, Title

DATABASE_ID = "57513fd292d3477d872099667f992636"


@notion_prop("名前")
class TasteName(Title): ...


@notion_prop("Tags")
class TasteTags(MultiSelect): ...


@notion_prop("一言コメント")
class TasteComment(Text): ...


@notion_prop("場所")
class TastePlace(Relation): ...


@notion_prop("感想")
class TasteImpression(Select): ...
