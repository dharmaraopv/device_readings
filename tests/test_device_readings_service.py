import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock
from stores.device_store import DeviceStoreIface
from stores.ts_store import TimeStampStoreIface
from models import DeviceReadings, Reading
from device_readings_service import DeviceReadingsService
from stores.in_mem_device_store import InMemoryDeviceStore
from stores.in_memory_ts_store import InMemoryTimestampStore


class TestDeviceReadingsService(unittest.TestCase):
    """
    Unit tests for the DeviceReadingsService class.

    This test case uses mock objects to isolate the DeviceReadingsService logic,
    allowing us to verify interactions and behaviors without depending on actual store implementations.
    """

    def setUp(self):
        # Mock the stores
        self.mock_device_store = Mock(spec=DeviceStoreIface)
        self.mock_ts_store = Mock(spec=TimeStampStoreIface)

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
        # Verifies that add_device_readings correctly adds readings when timestamps are new,
        # updating the count and timestamp as expected.

        mock_device_reading = Mock()
        self.mock_device_store.get_or_create_device_reading.return_value = mock_device_reading
        self.mock_ts_store.check_and_add_timestamp.side_effect = [True, True]

        result = self.service.add_device_readings(self.device_readings)

        self.assertEqual(result, "")
        mock_device_reading.increment_count.assert_any_call(3)
        mock_device_reading.increment_count.assert_any_call(2)
        mock_device_reading.update_latest_timestamp.assert_any_call(self.timestamp_1)
        mock_device_reading.update_latest_timestamp.assert_any_call(self.timestamp_2)

    def test_add_device_readings_partial_existing_timestamps(self):
        # Ensures that add_device_readings only adds readings for new timestamps,
        # without updating existing ones.

        mock_device_reading = Mock()
        self.mock_device_store.get_or_create_device_reading.return_value = mock_device_reading
        self.mock_ts_store.check_and_add_timestamp.side_effect = [True, False]

        result = self.service.add_device_readings(self.device_readings)

        self.assertEqual(result, "")
        mock_device_reading.increment_count.assert_called_once_with(3)
        mock_device_reading.update_latest_timestamp.assert_called_once_with(self.timestamp_1)

    def test_add_device_readings_device_store_error(self):
        # Checks that an error in retrieving or creating a device reading returns an appropriate error message.

        self.mock_device_store.get_or_create_device_reading.side_effect = ValueError("Device store error")

        result = self.service.add_device_readings(self.device_readings)
        self.assertEqual(result, "Device store error")

    def test_get_cumulative_count_success(self):
        # Validates that get_cumulative_count correctly retrieves the total count for an existing device reading.

        mock_device_reading = Mock()
        mock_device_reading.total_count = 10
        self.mock_device_store.get_device_reading.return_value = mock_device_reading

        count, error = self.service.get_cumulative_count(self.device_id)

        self.assertEqual(count, 10)
        self.assertIsNone(error)

    def test_get_cumulative_count_device_not_found(self):
        # Confirms that get_cumulative_count returns an error message when the device ID is not found.

        self.mock_device_store.get_device_reading.return_value = None

        count, error = self.service.get_cumulative_count(self.device_id)

        self.assertEqual(count, 0)
        self.assertEqual(error, f"Device with id {self.device_id} not found")

    def test_get_latest_timestamp_success(self):
        # Ensures that get_latest_timestamp retrieves the most recent timestamp for an existing device.

        mock_device_reading = Mock()
        mock_device_reading.latest_timestamp = self.timestamp_1
        self.mock_device_store.get_device_reading.return_value = mock_device_reading

        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        self.assertEqual(latest_timestamp, self.timestamp_1)
        self.assertIsNone(error)

    def test_get_latest_timestamp_device_not_found(self):
        # Checks that get_latest_timestamp returns an error message when the device ID is not found.

        self.mock_device_store.get_device_reading.return_value = None

        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        self.assertIsNone(latest_timestamp)
        self.assertEqual(error, f"Device with id {self.device_id} not found")


class TestDeviceReadingsServiceFunctional(unittest.TestCase):
    # This test case performs functional tests using the real in-memory stores,
    # validating that the DeviceReadingsService works correctly with actual data stores.

    def setUp(self):
        # Clear the in-memory stores before each test
        self.in_mem_device_store = InMemoryDeviceStore()
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
        # Tests that readings are added successfully, verifying total count and latest timestamp using real stores.

        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[
                Reading(timestamp=self.timestamp_1, count=3),
                Reading(timestamp=self.timestamp_2, count=2)
            ]
        )

        result = self.service.add_device_readings(device_readings)
        self.assertEqual(result, "")

        device_reading = self.in_mem_device_store.get_device_reading(self.device_id)

        self.assertEqual(device_reading.total_count, 5)
        self.assertEqual(device_reading.latest_timestamp, self.timestamp_2)

    def test_get_cumulative_count_functional(self):
        # Confirms that get_cumulative_count accurately retrieves the total count from the real in-memory store.

        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[Reading(timestamp=self.timestamp_1, count=4)]
        )
        self.service.add_device_readings(device_readings)

        count, error = self.service.get_cumulative_count(self.device_id)

        self.assertEqual(count, 4)
        self.assertIsNone(error)

    def test_get_latest_timestamp_functional(self):
        # Verifies that get_latest_timestamp correctly retrieves the most recent timestamp using real data.

        device_readings = DeviceReadings(
            id=self.device_id,
            readings=[
                Reading(timestamp=self.timestamp_1, count=2),
                Reading(timestamp=self.timestamp_2, count=3)
            ]
        )
        self.service.add_device_readings(device_readings)

        latest_timestamp, error = self.service.get_latest_timestamp(self.device_id)

        self.assertEqual(latest_timestamp, self.timestamp_2)
        self.assertIsNone(error)

    def test_device_not_found_functional(self):
        # Ensures that attempts to retrieve data for a non-existent device return appropriate error messages.

        count, count_error = self.service.get_cumulative_count(uuid.uuid4())
        self.assertEqual(count, 0)
        self.assertIsNotNone(count_error)

        latest_timestamp, ts_error = self.service.get_latest_timestamp(uuid.uuid4())
        self.assertIsNone(latest_timestamp)
        self.assertIsNotNone(ts_error)


if __name__ == '__main__':
    unittest.main()