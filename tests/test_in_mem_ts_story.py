import unittest
import uuid
from .test_utils import run_multiples_threads
from stores.in_memory_ts_store import InMemoryTimestampStore, _key


class TestInMemoryTimestampStore(unittest.TestCase):

    def setUp(self):
        self.capacity = 3
        self.store = InMemoryTimestampStore(capacity=self.capacity)
        self.device_id = uuid.uuid4()

    def test_add_timestamp(self):
        # Test that a new timestamp returns True (indicating it was added)
        timestamp = 1622540800
        result = self.store.check_and_add_timestamp(self.device_id, timestamp)
        self.assertTrue(result)
        self.assertIn(_key(self.device_id, timestamp), self.store.store)

    def test_add_existing_timestamp(self):
        # Test that an existing timestamp returns False
        timestamp = 1622540800
        self.store.check_and_add_timestamp(self.device_id, timestamp)
        result = self.store.check_and_add_timestamp(self.device_id, timestamp)
        self.assertFalse(result)

    def test_capacity(self):
        # Test that the store evicts the oldest entry when capacity is exceeded
        timestamps = [1622540800, 1622540900, 1622541000, 1622541100]
        for ts in timestamps:
            self.store.check_and_add_timestamp(self.device_id, ts)

        # Since capacity is 3, the first timestamp should be evicted
        oldest_key = _key(self.device_id, timestamps[0])
        self.assertNotIn(oldest_key, self.store.store)
        self.assertEqual(len(self.store.store), self.capacity)

    def test_capacity_with_different_device_ids(self):
        # Test that the store handles capacity with multiple device ids
        device_id_2 = uuid.uuid4()
        self.store.check_and_add_timestamp(self.device_id, 1622540800)
        self.store.check_and_add_timestamp(device_id_2, 1622540900)
        self.store.check_and_add_timestamp(self.device_id, 1622541000)
        self.store.check_and_add_timestamp(device_id_2, 1622541100)

        self.assertEqual(len(self.store.store), self.capacity)
        # Verify the oldest key is removed when capacity is exceeded
        self.assertNotIn(_key(self.device_id, 1622540800), self.store.store)

    def test_concurrent_addition_of_same_timestamp(self):
        # Test that concurrent addition of the same timestamp is handled correctly
        timestamp = 1622540800
        args = [(self.device_id,timestamp)] * 10
        result = run_multiples_threads(self.store.check_and_add_timestamp, args)
        count = 0
        for i in result:
            if i:
                count += 1
        self.assertEqual(count, 1)
        self.assertIn(_key(self.device_id, timestamp), self.store.store)

if __name__ == '__main__':
    unittest.main()