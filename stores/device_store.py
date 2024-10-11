import uuid
from abc import ABC, abstractmethod
from datetime import datetime


class DeviceReadingIface(ABC):
    """
    Abstract interface for a device reading.

    Attributes:
        total_count (int): The cumulative count of readings for a device.
        latest_timestamp (datetime): The latest timestamp when a reading was recorded.
    """
    total_count: int
    latest_timestamp: datetime

    @abstractmethod
    def increment_count(self, device_id: uuid.UUID):
        """
        Increment the count of readings for a specific device.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def update_latest_timestamp(self, device_id: uuid.UUID):
        """
        Update the timestamp of the latest reading for a specific device.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError


class DeviceStoreIface(ABC):
    """
    Abstract interface for a device store, responsible for managing device readings.
    """

    @abstractmethod
    def get_or_create_device_reading(self, device_id: uuid.UUID) -> DeviceReadingIface:
        """
        Retrieve an existing device reading or create a new one if it does not exist.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            DeviceReadingIface: The device reading instance associated with the device ID.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_reading(self, device_id: uuid.UUID) -> DeviceReadingIface:
        """
        Retrieve an existing device reading based on the device ID.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            DeviceReadingIface: The device reading instance associated with the device ID.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """
        Clear all device readings from the store.

        This can be used to reset the store, removing all device readings currently stored.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass