from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[..., Any]]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable[..., Any]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        event_type = type(event)
        for handler in self._handlers[event_type]:
            handler(event)
