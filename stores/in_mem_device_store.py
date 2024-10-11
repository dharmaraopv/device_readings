import datetime
import uuid
from threading import Lock

from pydantic import BaseModel
from config import settings

from stores.device_store import DeviceReadingBase, DeviceStoreBase


class DeviceReading(BaseModel, DeviceReadingBase):
    device_id: uuid.UUID
    latest_timestamp: datetime.datetime = None
    total_count: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self._lock = Lock()

    def increment_count(self, count):
        self.total_count += count

    def update_timestamp(self, timestamp):
        with self._lock:
            if not self.latest_timestamp or timestamp > self.latest_timestamp:
                self.latest_timestamp = timestamp


class DeviceStore(DeviceStoreBase):
    def __init__(self, capacity=1):
        self._init_store()
        self.capacity = capacity

    def _init_store(self):
        self.store = {}
    def _manage_capacity(self):
        if len(self.store) > self.capacity:
            # Remove the latest item
            self.store.popitem()
            raise ValueError("Capacity exceeded")

    def get_or_create_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        device_reading = self.store.setdefault(device_id, DeviceReading(device_id=device_id))
        self._manage_capacity()

        return device_reading

    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        return self.store.get(device_id)

    def clear(self):
        self._init_store()


in_mem_device_store = DeviceStore(capacity=settings.DEVICE_STORE_CAPACITY)
