from lotion import notion_prop
from lotion.properties import Checkbox, Date, MultiSelect, Select, Text, Title

DATABASE_ID = "e4661e93d9a04fa282d58b1433860ce9"


@notion_prop("Name")
class ObsidianName(Title): ...


@notion_prop("ステータス")
class ObsidianStatus(Select): ...


@notion_prop("タグ")
class ObsidianTags(MultiSelect): ...


@notion_prop("プロジェクトセッション")
class ObsidianIsProjectSession(Checkbox): ...


@notion_prop("プロジェクト名")
class ObsidianProjectName(Text): ...


@notion_prop("作成日")
class ObsidianCreatedDate(Date): ...
