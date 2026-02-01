from typing import TYPE_CHECKING, Any

from lotion import BasePage, Lotion, notion_database, notion_prop
from lotion.properties import Checkbox, MultiSelect, Select, Title

if TYPE_CHECKING:
    from sandpiper.shared.model.someday_item import SomedayItem

DATABASE_ID = "2db6567a3bbf80a8b3f3e3560cfe380f"


@notion_prop("名前")
class SomedayName(Title):  # type: ignore[misc]
    ...


@notion_prop("タイミング")
class SomedayTiming(Select):  # type: ignore[misc]
    ...


@notion_prop("明日やる")
class SomedayDoTomorrow(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("論理削除")
class SomedayIsDeleted(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("コンテクスト")
class SomedayContext(MultiSelect):  # type: ignore[misc]
    ...


@notion_database(DATABASE_ID)
class SomedayPage(BasePage):  # type: ignore[misc]
    name: SomedayName
    timing: SomedayTiming
    do_tomorrow: SomedayDoTomorrow
    is_deleted: SomedayIsDeleted
    context: SomedayContext

    @staticmethod
    def generate(item: "SomedayItem") -> "SomedayPage":
        properties: list[Any] = [
            SomedayName.from_plain_text(item.title),
            SomedayTiming.from_name(item.timing.value),
            SomedayDoTomorrow.true() if item.do_tomorrow else SomedayDoTomorrow.false(),
            SomedayIsDeleted.true() if item.is_deleted else SomedayIsDeleted.false(),
        ]
        if item.context:
            properties.append(SomedayContext.from_name(item.context))
        return SomedayPage.create(properties=properties)  # type: ignore[no-any-return]

    def to_domain(self) -> "SomedayItem":
        from sandpiper.shared.model.someday_item import SomedayItem
        from sandpiper.shared.valueobject.someday_timing import SomedayTiming as DomainSomedayTiming

        timing_name = self.timing.selected_name if self.timing else None
        timing = DomainSomedayTiming.TOMORROW if timing_name == "明日" else DomainSomedayTiming.SOMEDAY
        do_tomorrow = self.do_tomorrow.checked if self.do_tomorrow else False
        is_deleted = self.is_deleted.checked if self.is_deleted else False
        context = [v.name for v in self.context.values] if self.context else []

        return SomedayItem(
            id=self.id,
            title=self.get_title_text(),
            timing=timing,
            do_tomorrow=do_tomorrow,
            is_deleted=is_deleted,
            context=context,
        )

    @staticmethod
    def fetch_all(client: Lotion | None = None) -> list["SomedayPage"]:
        lotion = client or Lotion.get_instance()
        return lotion.retrieve_database(DATABASE_ID, cls=SomedayPage)  # type: ignore[no-any-return]
