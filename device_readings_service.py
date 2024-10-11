from stores.device_store import DeviceStoreIface
from stores.in_mem_device_store import in_mem_device_store
from stores.in_memory_ts_store import in_mem_ts_store
from stores.ts_store import TimeStampStoreIface
from models import DeviceReadings

import uuid
from datetime import datetime


class DeviceReadingsService:
    """
    Service layer for handling operations related to device readings.

    This class provides methods for adding readings to a device, retrieving cumulative counts,
    and getting the latest timestamp for a device. It relies on external storage interfaces
    for managing device data and timestamps.
    """

    def __init__(self, device_store: DeviceStoreIface, ts_store: TimeStampStoreIface):
        """
        Initialize the DeviceReadingsService with a device store and a timestamp store.

        Args:
            device_store (DeviceStoreIface): The store interface for managing device readings.
            ts_store (TimeStampStoreIface): The store interface for managing timestamps.
        """
        self.device_store = device_store
        self.ts_store = ts_store

    def add_device_readings(self, device_readings: DeviceReadings) -> str:
        """
        Add readings to a device, updating the count and timestamp as necessary.

        This method checks if each reading's timestamp is new and, if so, updates the device's
        cumulative count and latest timestamp. If the device entry cannot be created, a
        ValueError is raised.

        Args:
            device_readings (DeviceReadings): The readings to be added for a specific device.

        Returns:
            str: An empty string if successful, or an error message if the device cannot be created.
        """
        try:
            device_reading = self.device_store.get_or_create_device_reading(device_readings.id)
        except ValueError as e:
            return str(e)

        # Process each reading for the device
        for reading in device_readings.readings:
            # Convert timestamp to Unix epoch format for storage and checking
            if self.ts_store.check_and_add_timestamp(device_readings.id, reading.timestamp.timestamp()):
                device_reading.increment_count(reading.count)
                device_reading.update_latest_timestamp(reading.timestamp)

        return ""

    def get_cumulative_count(self, device_id: uuid.UUID) -> (int, str):
        """
        Retrieve the cumulative count of readings for a given device.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            tuple: A tuple containing the cumulative count (int) and an error message (str) if the device is not found.
        """
        device_reading = self.device_store.get_device_reading(device_id)
        if not device_reading:
            return 0, f"Device with id {device_id} not found"
        return device_reading.total_count, None

    def get_latest_timestamp(self, device_id: uuid.UUID) -> (datetime, str):
        """
        Retrieve the latest timestamp of readings for a given device.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.

        Returns:
            tuple: A tuple containing the latest timestamp (datetime) and an error message (str) if the device is not found.
        """
        device_reading = self.device_store.get_device_reading(device_id)
        if not device_reading:
            return None, f"Device with id {device_id} not found"
        return device_reading.latest_timestamp, None


# Initialize the DeviceReadingsService with in-memory stores.
device_readings_service = DeviceReadingsService(device_store=in_mem_device_store, ts_store=in_mem_ts_store)