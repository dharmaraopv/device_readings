import datetime
import uuid
from threading import Lock

from pydantic import BaseModel, ValidationError

from stores.device_store import DeviceReadingBase


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


class DeviceStore:
    def __init__(self, capacity=1000):
        self.store = {}
        self.capacity = capacity

    def manage_capacity(self):
        if len(self.store) > self.capacity:
            # Remove the latest item
            self.store.popitem()
            raise ValueError("Capacity exceeded")

    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        device_reading = self.store.setdefault(device_id, DeviceReading(device_id=device_id))
        self.manage_capacity()
        return device_reading
