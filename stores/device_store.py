import uuid
from abc import ABC, abstractmethod


class DeviceReadingBase(ABC):
    @abstractmethod
    def increment_count(self, device_id: uuid.UUID):
        raise NotImplementedError

    @abstractmethod
    def update_timestamp(self, device_id: uuid.UUID):
        raise NotImplementedError
class DeviceStoreBase(ABC):
    @abstractmethod
    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        """
        Get the device reading from the store.
        """
        raise NotImplementedError
