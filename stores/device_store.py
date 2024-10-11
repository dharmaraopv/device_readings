import uuid
from abc import ABC, abstractmethod
from datetime import datetime


class DeviceReadingBase(ABC):
    total_count: int
    latest_timestamp: datetime

    @abstractmethod
    def increment_count(self, device_id: uuid.UUID):
        raise NotImplementedError

    @abstractmethod
    def update_timestamp(self, device_id: uuid.UUID):
        raise NotImplementedError


class DeviceStoreBase(ABC):
    @abstractmethod
    def get_or_create_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        """
        Get the device reading from the store.
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingBase:
        """
        Get the device reading from the store.
        """
        raise NotImplementedError
