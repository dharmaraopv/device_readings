from stores.device_store import DeviceStoreBase
from stores.in_mem_device_store import in_mem_device_store
from stores.in_memory_ts_store import in_mem_ts_store
from stores.ts_store import TimeStampStore
from models import DeviceReadings

import uuid
from datetime import datetime


class DeviceReadingsService:
    def __init__(self, device_store: DeviceStoreBase, ts_store: TimeStampStore):
        self.device_store = device_store
        self.ts_store = ts_store

    def add_device_readings(self, device_readings: DeviceReadings) -> str:
        try:
            device_reading = self.device_store.get_or_create_device_reading(device_readings.id)
        except ValueError as e:
            return str(e)

        for reading in device_readings.readings:
            if self.ts_store.check_and_add_timestamp(device_readings.id, reading.timestamp):
                device_reading.increment_count(reading.count)
                device_reading.update_timestamp(reading.timestamp)

        return ""

    def get_cumulative_count(self, device_id: uuid.UUID) -> (int, str):
        device_reading = self.device_store.get_device_reading(device_id)
        if not device_reading:
            return 0, f"Device with id {device_id} not found"
        return device_reading.total_count, None

    def get_latest_timestamp(self, device_id: uuid.UUID) -> (datetime, str):
        device_reading = self.device_store.get_device_reading(device_id)
        if not device_reading:
            return None, f"Device with id {device_id} not found"
        return device_reading.latest_timestamp, None


device_readings_service = DeviceReadingsService(device_store=in_mem_device_store, ts_store=in_mem_ts_store)
