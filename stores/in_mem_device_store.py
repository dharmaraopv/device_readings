import datetime
import uuid
from threading import Lock

from pydantic import BaseModel
from config import settings

from stores.device_store import DeviceReadingIface, DeviceStoreIface


class DeviceReading(BaseModel, DeviceReadingIface):
    """
    Concrete implementation of the DeviceReadingIface, representing a device reading.

    Attributes:
        device_id (uuid.UUID): The unique identifier of the device.
        latest_timestamp (datetime.datetime): The most recent timestamp when a reading was recorded.
        total_count (int): The cumulative count of readings for the device.
    """
    device_id: uuid.UUID
    latest_timestamp: datetime.datetime = None
    total_count: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self._lock = Lock()  # Thread-safe lock for updating timestamp

    def increment_count(self, count):
        """
        Increment the total count of readings by the given count.

        This operation is thread-safe because GIL ensures atomicity of the operation.

        Args:
            count (int): The number of readings to add to the total count.
        """
        self.total_count += count

    def update_latest_timestamp(self, timestamp):
        """
        Update the latest timestamp for the reading, ensuring thread safety with a lock.

        Args:
            timestamp (datetime.datetime): The new timestamp to set.
        """
        with self._lock:
            # Only update if the new timestamp is more recent
            if not self.latest_timestamp or timestamp > self.latest_timestamp:
                self.latest_timestamp = timestamp


class InMemoryDeviceStore(DeviceStoreIface):
    """
    Concrete implementation of DeviceStoreIface, managing device readings with a fixed capacity.

    Attributes:
        capacity (int): The maximum number of device readings the store can hold.
    """

    def __init__(self, capacity=100):
        """
        Initialize the InMemoryDeviceStore with a specified capacity.

        Args:
            capacity (int): The maximum number of device readings to store.
        """
        self._init_store()
        self.capacity = capacity

    def _init_store(self):
        """Initialize/Reset the internal storage for device readings."""
        self.store = {}

    def _manage_capacity(self):
        """
        Ensure the store does not exceed its capacity by removing the new entry if needed.

        Raises:
            ValueError: If the store exceeds the defined capacity.
        """
        if len(self.store) > self.capacity:
            self.store.popitem()  # Remove the oldest entry
            raise ValueError("Capacity exceeded")

    def get_or_create_device_reading(self, device_id: uuid.UUID) -> DeviceReadingIface:
        """
        Retrieve an existing DeviceReading for the specified device ID, or create a new one if it doesn't exist.

        Thread safety is guaranteed because the GIL ensures atomicity of the setdefault operation.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            DeviceReadingIface: The device reading instance for the specified device.
        """
        device_reading = self.store.setdefault(device_id, DeviceReading(device_id=device_id))
        self._manage_capacity()
        return device_reading

    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingIface:
        """
        Retrieve the DeviceReading for the specified device ID, if it exists.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            DeviceReadingIface: The device reading instance, or None if it does not exist.
        """
        return self.store.get(device_id)

    def clear(self):
        """Clear all device readings from the store, resetting it to an empty state."""
        self._init_store()


# Initialize an in-memory device store with the capacity defined in settings.
in_mem_device_store = InMemoryDeviceStore(capacity=settings.DEVICE_STORE_CAPACITY)
