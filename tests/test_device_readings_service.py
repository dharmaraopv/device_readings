import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock
from stores.device_store import DeviceStoreBase
from stores.ts_store import TimeStampStore
from models import DeviceReadings, Reading
from device_readings_service import DeviceReadingsService  # Replace 'your_module' with the actual module name


class TestDeviceReadingsService(unittest.TestCase):

    def setUp(self):
        # Mock the stores
        self.mock_device_store = Mock(spec=DeviceStoreBase)
        self.mock_ts_store = Mock(spec=TimeStampStore)

        # Instantiate the service with mocked stores
        self.service = DeviceReadingsService(
            device_store=self.mock_device_store,
            ts_store=self.mock_ts_store
        )

        # Setup common test data
        self.device_id = uuid.uuid4()
        self.timestamp_1 = datetime.now()
        self.timestamp_2 = self.timestamp_1 + timedelta(seconds=10)

        # Setup DeviceReadings object with multiple readings
        self.device_readings = DeviceReadings(
            id=self.device_id,
            readings=[
                Reading(timestamp=self.timestamp_1, count=3),
                Reading(timestamp=self.timestamp_2, count=2)
            ]
        )

    def test_add_device_readings_success(self):
        # Mock return values
        mock_device_reading = Mock()
        self.mock_device_store.get_or_create_device_reading.return_value = mock_device_reading
        self.mock_ts_store.check_and_add_timestamp.side_effect = [True, True]

        # Call add_device_readings
        result = self.service.add_device_readings(self.device_readings)

        # Assert expected behavior
        self.assertEqual(result, "")
        mock_device_reading.increment_count.assert_any_call(3)
        mock_device_reading.increment_count.assert_any_call(2)
        mock_device_reading.update_timestamp.assert_any_call(self.timestamp_1)
        mock_device_reading.update_timestamp.assert_any_call(self.timestamp_2)

    def test_add_device_readings_partial_existing_timestamps(self):
        # Mock one timestamp to be new and one to be existing
        mock_device_reading = Mock()
        self.mock_device_store.get_or_create_device_reading.return_value = mock_device_reading
        self.mock_ts_store.check_and_add_timestamp.side_effect = [True, False]

        # Call add_device_readings
        result = self.service.add_device_readings(self.device_readings)

        # Assert expected behavior
        self.assertEqual(result, "")
        mock_device_reading.increment_count.assert_called_once_with(3)
        mock_device_reading.update_timestamp.assert_called_once_with(self.timestamp_1)

    def test_add_device_readings_device_store_error(self):
        # Simulate device store raising a ValueError
        self.mock_device_store.get_or_create_device_reading.side_effect = ValueError("Device store error")

        # Call add_device_readings and check for the error message
        result = self.service.add_device_readings(self.device_readings)
        self.assertEqual(result, "Device store error")

    def test_get_cumulative_count_success(self):
        # Mock total count on the device reading
        mock_device_reading = Mock()
        mock_device_reading.total_count = 10
        self.mock_device_store.get_device_reading.return_value = mock_device_reading

        # Call get_cumulative_count
        count, error = self.service.get_cumulative_count(self.device_id)

        # Verify results
        self.assertEqual(count, 10)
        self.assertIsNone(error)

    def test_get_cumulative_count_device_not_found(self):
        # Mock device not found scenario
        self.mock_device_store.get_device_reading.return_value = None

        # Call get_cumulative_count
        count, error = self.service.get_cumulative_count(self.device_id)

        # Verify error message
        self.assertEqual(count, 0)
        self.assertEqual(error, f"Device with id {self.device_id} not found")

    def test_get_latest_timestamp_success(self):
        # Mock latest timestamp on the device reading
        mock_device_reading = Mock()
        mock_device_reading.latest_timestamp = self.timestamp_1
        self.mock_device_store.get_device_reading.return_value = mock_device_reading

        # Call get_latest_timestamp
        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        # Verify results
        self.assertEqual(latest_timestamp, self.timestamp_1)
        self.assertIsNone(error)

    def test_get_latest_timestamp_device_not_found(self):
        # Mock device not found scenario
        self.mock_device_store.get_device_reading.return_value = None

        # Call get_latest_timestamp
        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        # Verify error message
        self.assertIsNone(latest_timestamp)
        self.assertEqual(error, f"Device with id {self.device_id} not found")


from stores.in_mem_device_store import DeviceStore
from stores.in_memory_ts_store import InMemoryTimestampStore


class TestDeviceReadingsServiceFunctional(unittest.TestCase):

    def setUp(self):
        # Clear the in-memory stores before each test
        self.in_mem_device_store = DeviceStore()
        self.in_mem_ts_store = InMemoryTimestampStore()

        # Initialize DeviceReadingsService with in-memory stores
        self.service = DeviceReadingsService(
            device_store=self.in_mem_device_store,
            ts_store=self.in_mem_ts_store
        )

        # Setup common test data
        self.device_id = uuid.uuid4()
        self.timestamp_1 = datetime.now()
        self.timestamp_2 = self.timestamp_1 + timedelta(seconds=10)

    def test_add_device_readings_functional(self):
        # Create DeviceReadings with two readings
        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[
                Reading(timestamp=self.timestamp_1, count=3),
                Reading(timestamp=self.timestamp_2, count=2)
            ]
        )

        # Add device readings
        result = self.service.add_device_readings(device_readings)

        # Verify no errors occurred
        self.assertEqual(result, "")

        # Retrieve device reading from the device store to verify state
        device_reading = self.in_mem_device_store.get_device_reading(self.device_id)

        # Verify total count and latest timestamp
        self.assertEqual(device_reading.total_count, 5)
        self.assertEqual(device_reading.latest_timestamp, self.timestamp_2)

    def test_get_cumulative_count_functional(self):
        # Add initial reading
        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[Reading(timestamp=self.timestamp_1, count=4)]
        )
        self.service.add_device_readings(device_readings)

        # Get cumulative count
        count, error = self.service.get_cumulative_count(self.device_id)

        # Verify count and no error message
        self.assertEqual(count, 4)
        self.assertIsNone(error)

    def test_get_latest_timestamp_functional(self):
        # Add multiple readings
        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[
                Reading(timestamp=self.timestamp_1, count=2),
                Reading(timestamp=self.timestamp_2, count=3)
            ]
        )
        self.service.add_device_readings(device_readings)

        # Retrieve the latest timestamp
        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        # Verify latest timestamp and no error message
        self.assertEqual(latest_timestamp, self.timestamp_2)
        self.assertIsNone(error)

    def test_device_not_found_functional(self):
        # Attempt to get cumulative count for a non-existing device
        count, count_error = self.service.get_cumulative_count(uuid.uuid4())
        self.assertEqual(count, 0)
        self.assertIsNotNone(count_error)

        # Attempt to get latest timestamp for a non-existing device
        latest_timestamp, ts_error = self.service.get_latest_timestamp(uuid.uuid4())
        self.assertIsNone(latest_timestamp)
        self.assertIsNotNone(ts_error)


if __name__ == '__main__':
    unittest.main()