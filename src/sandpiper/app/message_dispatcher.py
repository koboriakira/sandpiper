from sandpiper.shared.infrastructure.event_bus import EventBus


class MessageDispatcher:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def publish(self, message: object):
        self._event_bus.publish(message)
