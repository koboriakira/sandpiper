from collections import defaultdict
from collections.abc import Callable


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable):
        self._handlers[event_type].append(handler)

    def publish(self, event: object):
        event_type = type(event)
        for handler in self._handlers[event_type]:
            handler(event)
