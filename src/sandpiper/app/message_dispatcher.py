from sandpiper.shared.infrastructure.event_bus import EventBus


class MessageDispatcher:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    def publish(self, message: object) -> None:
        self._event_bus.publish(message)
