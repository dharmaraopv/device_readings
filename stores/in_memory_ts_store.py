import uuid
from collections import OrderedDict
from .ts_store import TimeStampStoreIface
from config import settings


def _key(device_id, timestamp):
    """
    Generate a unique key based on device ID and timestamp.

    Args:
        device_id (uuid.UUID): The unique identifier of the device.
        timestamp (int): The timestamp in Unix epoch format.

    Returns:
        str: A unique key combining the device ID and timestamp.
    """
    return f"{device_id}-{timestamp}"


class InMemoryTimestampStore(TimeStampStoreIface):
    """
    In-memory store for managing timestamps per device ID.

    This store keeps a fixed number of timestamps and automatically evicts the oldest
    timestamp when the capacity is exceeded. It uses an ordered dictionary to maintain
    the insertion order and efficiently remove the oldest item when necessary.

    Attributes:
        capacity (int): The maximum number of timestamps to store.
    """

    def __init__(self, capacity=1000):
        """
        Initialize the InMemoryTimestampStore with a specified capacity.

        Args:
            capacity (int): The maximum number of timestamps to store. Defaults to 1000.
        """
        self.capacity = capacity
        self._init_store()

    def _init_store(self):
        """Initialize the internal ordered dictionary to store timestamps."""
        self.store = OrderedDict()

    def __repr__(self):
        """
        Return a string representation of the timestamp store.

        Returns:
            str: A string representing the current state of the store.
        """
        return f"TimeStampStore({self.store})"

    def check_and_add_timestamp(self, device_id: uuid.UUID, timestamp: int) -> bool:
        """
        Check if a timestamp is present and add it to the store if not.

        If the timestamp is not already in the store, it is added, and the method
        returns True. Otherwise, it returns False. This method also manages the
        capacity of the store, evicting the oldest timestamp if necessary.

        Atomicity is ensured with the use of setdefault operation.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.
            timestamp (int): The timestamp in Unix epoch format.

        Returns:
            bool: True if the timestamp was added, False if it was already present.
        """
        key = _key(device_id, timestamp)
        some_unique_value = object()  # Placeholder for unique value
        existing = self.store.setdefault(key, some_unique_value)

        self._maintain_capacity(key)  # Ensure store remains within capacity

        return existing is some_unique_value

    def clear(self):
        """Clear all timestamps from the store, resetting it to an empty state."""
        self._init_store()

    def _maintain_capacity(self, key):
        """
        Maintain the capacity of the store by evicting the oldest timestamp if needed.

        Moves the given key to the end of the ordered dictionary to mark it as the most recent.
        If the store exceeds its capacity, it removes the oldest item (the first item).

        Args:
            key (str): The key corresponding to the most recent timestamp.
        """
        self.store.move_to_end(key)
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)  # Remove the oldest entry


# Initialize an in-memory timestamp store with the configured capacity.
in_mem_ts_store = InMemoryTimestampStore(capacity=settings.TIMESTAMP_STORE_CAPACITY)