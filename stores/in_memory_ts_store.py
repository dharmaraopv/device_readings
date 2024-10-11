import uuid
from collections import OrderedDict
from .ts_store import TimeStampStore
from config import settings


def _key(device_id, timestamp):
    return f"{device_id}-{timestamp}"


class InMemoryTimestampStore(TimeStampStore):
    """
    In-memory store for timestamps per device id.

    The store maintains a fixed capacity and evicts the oldest timestamp if the capacity is exceeded.
    """

    def __init__(self, capacity=1000):
        self.capacity = capacity

        self._init_store()

    def _init_store(self):
        self.store = OrderedDict()

    def __repr__(self):
        return f"TimeStampStore({self.store})"

    def check_and_add_timestamp(self, device_id: uuid.UUID, timestamp: int) -> bool:
        """
        Check if the timestamp is already present in the store.
        Add the timestamp to the store and return True if it is not present.
        :param device_id: UUID of the device
        :param timestamp: timestamp to be checked in unix epoch format
        :return: bool
        """
        key = _key(device_id, timestamp)
        some_unique_value = object()
        existing = self.store.setdefault(key, some_unique_value)

        self._maintain_capacity(key)

        return existing is some_unique_value

    def clear(self):
        self._init_store()

    def _maintain_capacity(self, key):
        self.store.move_to_end(key)
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)



in_mem_ts_store = InMemoryTimestampStore(capacity=settings.TIMESTAMP_STORE_CAPACITY)
