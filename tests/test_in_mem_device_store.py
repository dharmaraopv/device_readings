import random
import unittest
import uuid
import datetime
from stores.device_store import DeviceReadingIface
from stores.in_mem_device_store import DeviceReading, InMemoryDeviceStore  # Replace 'your_module' with the actual module name
from tests.utils import run_multiples_threads


class TestDeviceReading(unittest.TestCase):

    def setUp(self):
        self.device_id = uuid.uuid4()
        self.device_reading = DeviceReading(device_id=self.device_id)

    def test_initialization(self):
        # Check that the DeviceReading object initializes correctly
        self.assertEqual(self.device_reading.device_id, self.device_id)
        self.assertEqual(self.device_reading.total_count, 0)
        self.assertEqual(self.device_reading.latest_timestamp, None)

    def test_increment_count(self):
        # Verify that increment_count correctly increases the total count
        self.device_reading.increment_count(5)
        self.assertEqual(self.device_reading.total_count, 5)
        self.device_reading.increment_count(3)
        self.assertEqual(self.device_reading.total_count, 8)

    def test_increment_count_concurrent(self):
        # Verify that increment_count correctly increases the total count with concurrent calls
        args = [[5]] * 100
        run_multiples_threads(self.device_reading.increment_count, args)
        self.assertEqual(self.device_reading.total_count, 500)

    def test_update_timestamp(self):
        # Test that update_latest_timestamp correctly updates the latest timestamp if it is newer
        old_timestamp = datetime.datetime.now()
        self.device_reading.update_latest_timestamp(old_timestamp)
        self.assertEqual(self.device_reading.latest_timestamp, old_timestamp)

        new_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.device_reading.update_latest_timestamp(new_timestamp)
        self.assertEqual(self.device_reading.latest_timestamp, new_timestamp)

        # Check that it does not update if the timestamp is older
        older_timestamp = datetime.datetime.now() - datetime.timedelta(seconds=5)
        self.device_reading.update_latest_timestamp(older_timestamp)
        self.assertEqual(self.device_reading.latest_timestamp, new_timestamp)

    def test_update_timestamp_concurrent(self):
        # Verify that update_latest_timestamp correctly updates the latest timestamp with concurrent calls
        old_timestamp = datetime.datetime.now()
        args = [[old_timestamp + datetime.timedelta(seconds=10)*i] for i in range(10)]
        highest_timestamp = args[-1][0]
        random.shuffle(args)
        run_multiples_threads(self.device_reading.update_latest_timestamp, args)
        self.assertEqual(self.device_reading.latest_timestamp, highest_timestamp)


class TestDeviceStore(unittest.TestCase):

    def setUp(self):
        self.device_store = InMemoryDeviceStore(capacity=2)
        self.device_id_1 = uuid.uuid4()
        self.device_id_2 = uuid.uuid4()
        self.device_id_3 = uuid.uuid4()

    def test_initialization(self):
        # Ensure the InMemoryDeviceStore initializes with the correct capacity
        self.assertEqual(self.device_store.capacity, 2)
        self.assertEqual(len(self.device_store.store), 0)

    def test_get_or_create_device_reading(self):
        # Test that get_or_create_device_reading returns a DeviceReading object and adds it to the store
        reading = self.device_store.get_or_create_device_reading(self.device_id_1)
        self.assertIsInstance(reading, DeviceReadingIface)
        self.assertIn(self.device_id_1, self.device_store.store)

    def test_manage_capacity_exceeds(self):
        # Add readings up to the capacity and ensure that exceeding capacity raises ValidationError
        self.device_store.get_or_create_device_reading(self.device_id_1)
        self.device_store.get_or_create_device_reading(self.device_id_2)
        with self.assertRaises(ValueError) as exc_info:
            self.device_store.get_or_create_device_reading(self.device_id_3)
        self.assertEqual(str(exc_info.exception), "Capacity exceeded")
        self.assertEqual(len(self.device_store.store), 2)

    def test_store_maintains_capacity(self):
        # Add more readings than capacity and verify store size is maintained at capacity limit
        self.device_store.get_or_create_device_reading(self.device_id_1)
        self.device_store.get_or_create_device_reading(self.device_id_2)
        try:
            self.device_store.get_or_create_device_reading(self.device_id_3)
        except ValueError:
            pass  # ValidationError expected due to capacity exceedance

        self.assertEqual(len(self.device_store.store), 2)

    def test_get_device_reading(self):
        # Test that get_device_reading returns a DeviceReading object if it exists in the store
        self.device_store.get_or_create_device_reading(self.device_id_1)
        reading = self.device_store.get_device_reading(self.device_id_1)
        self.assertIsInstance(reading, DeviceReadingIface)
        self.assertEqual(reading.device_id, self.device_id_1)

    def test_get_device_reading_non_existent(self):
        # Test that get_device_reading returns None if the device_id does not exist in the store
        reading = self.device_store.get_device_reading(self.device_id_2)
        self.assertIsNone(reading)


if __name__ == '__main__':
    unittest.main()