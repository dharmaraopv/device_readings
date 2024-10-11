import datetime
import unittest
import uuid
import random

from main import app
from fastapi.testclient import TestClient
from config import settings
from device_readings_service import device_readings_service


class E2ETests(unittest.TestCase):
    """
    End-to-end tests for the device readings API.

    This test suite verifies the integration and functionality of the main API endpoints in the application.
    It uses FastAPI's TestClient to simulate HTTP requests and tests scenarios such as:

    - Adding device readings and retrieving cumulative counts and timestamps.
    - Handling duplicate timestamps both within the same request and across multiple requests.
    - Enforcing device store capacity limits and verifying error messages when exceeded.
    - Ensuring each device maintains independent readings and can handle multiple devices simultaneously.
    - Validating correct responses for unknown device requests.
    - Ensuring the correct handling of out-of-order timestamps without overriding the most recent entry.

    The setUp method initializes the required objects and default data, while tearDown clears the in-memory
    stores to ensure each test starts with a clean state.
    """
    def setUp(self):
        # Initialize test client and set up test data
        self.client = TestClient(app)
        self.device_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        self.unknown_device_id = "3fa85f64-5717-4562-b3fc-2c963f66afa7"
        self.timestamp = "2024-10-11T02:11:43.862000+00:00"
        self.data = {
            "id": self.device_id,
            "readings": [
                {
                    "timestamp": self.timestamp,
                    "count": 15
                }
            ]
        }

    def tearDown(self):
        # Clear the stores after each test to ensure clean state
        device_readings_service.device_store.clear()
        device_readings_service.ts_store.clear()

    def test_update_readings_and_fetch_responses(self):
        # Test that readings can be added and then fetched for cumulative count and latest timestamp

        # Add a reading
        response = self.client.post("/api/devices/readings", json=self.data)
        # Verify successful addition of the reading
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Readings updated successfully"})

        # Fetch cumulative count for the device
        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        # Verify cumulative count matches the count added
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})

        # Fetch latest timestamp for the device
        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        # Verify latest timestamp matches the timestamp added
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"latest_timestamp": self.timestamp})

    def test_fetch_counts_for_unknown_device(self):
        # Test that fetching cumulative count for an unknown device returns a 404 error

        # Attempt to fetch cumulative count for an unknown device
        response = self.client.get(f"/api/devices/{self.unknown_device_id}/cumulative_count")
        # Verify response is a 404 with appropriate error message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": f"Device with id {self.unknown_device_id} not found"})

    def test_fetch_latest_timestamp_for_unknown_device(self):
        # Test that fetching the latest timestamp for an unknown device returns a 404 error

        # Attempt to fetch latest timestamp for an unknown device
        response = self.client.get(f"/api/devices/{self.unknown_device_id}/latest_timestamp")
        # Verify response is a 404 with appropriate error message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": f"Device with id {self.unknown_device_id} not found"})

    def test_error_message_after_device_capacity_is_reached(self):
        # Test that exceeding the device capacity returns a capacity exceeded error

        # Add readings up to the device store capacity
        for _ in range(settings.DEVICE_STORE_CAPACITY):
            data = {
                "id": str(uuid.uuid4()),
                "readings": [
                    {
                        "timestamp": self.timestamp,
                        "count": 15
                    }
                ]
            }
            response = self.client.post("/api/devices/readings", json=data)
            # Verify each addition is successful
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Readings updated successfully"})

        # Attempt to add one more reading, exceeding capacity
        response = self.client.post("/api/devices/readings", json=self.data)
        # Verify response indicates capacity has been exceeded
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"message": "Capacity exceeded"})

    def test_duplicate_timestamps_in_same_request(self):
        # Test that duplicate timestamps in the same request are only counted once

        # Prepare data with duplicate timestamps
        data = {
            "id": self.device_id,
            "readings": [
                {
                    "timestamp": self.timestamp,
                    "count": 15
                },
                {
                    "timestamp": self.timestamp,
                    "count": 15
                }
            ]
        }
        # Add readings with duplicate timestamps
        response = self.client.post("/api/devices/readings", json=data)
        # Verify successful addition of readings
        self.assertEqual(response.status_code, 200)

        # Fetch cumulative count for the device
        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        # Verify that only one reading was counted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})

    def test_duplicate_timestamps_multiple_requests(self):
        # Test that duplicate timestamps across multiple requests are only counted once

        data = {
            "id": self.device_id,
            "readings": [
                {
                    "timestamp": self.timestamp,
                    "count": 15
                }
            ]
        }

        # First request to add a reading
        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        # Second request with the same timestamp
        response = self.client.post("/api/devices/readings", json=data)
        # Verify successful addition without duplicate counting
        self.assertEqual(response.status_code, 200)

        # Fetch cumulative count for the device
        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        # Verify that only one reading was counted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})

    def test_out_of_order_timestamps(self):
        # Test that an older timestamp does not override a more recent timestamp

        now = datetime.datetime.now()
        now_string = now.isoformat()
        past_string = (now - datetime.timedelta(seconds=10)).isoformat()

        # Add a reading with the current timestamp
        data = {
            "id": self.device_id,
            "readings": [
                {
                    "timestamp": now_string,
                    "count": 15
                },
            ]
        }
        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        # Attempt to add an older timestamp
        data["readings"][0]["timestamp"] = past_string
        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        # Fetch latest timestamp to confirm it's still the most recent
        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"latest_timestamp": now_string})

    def test_multiple_devices(self):
        # Test that multiple devices can store and retrieve their readings independently

        devices_data = {}
        # Add readings for multiple devices
        for i in range(min(5, settings.DEVICE_STORE_CAPACITY)):
            data = {
                "id": str(uuid.uuid4()),
                "readings": [
                    {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "count": random.randint(1, 100)
                    }
                ]
            }
            devices_data[data["id"]] = data
            response = self.client.post("/api/devices/readings", json=data)
            # Verify successful addition for each device
            self.assertEqual(response.status_code, 200)

        # Check readings for each device
        for device_id, data in devices_data.items():
            # Verify cumulative count
            response = self.client.get(f"/api/devices/{device_id}/cumulative_count")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"cumulative_count": data["readings"][0]["count"]})

            # Verify latest timestamp
            response = self.client.get(f"/api/devices/{device_id}/latest_timestamp")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"latest_timestamp": data["readings"][0]["timestamp"]})