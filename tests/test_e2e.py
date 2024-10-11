import datetime
import unittest
import uuid
import random

from main import app
from fastapi.testclient import TestClient
from config import settings
from device_readings_service import device_readings_service


class E2ETests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.device_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        self.unknown_device_id ="3fa85f64-5717-4562-b3fc-2c963f66afa7"
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
        device_readings_service.device_store.clear()
        device_readings_service.ts_store.clear()

    def test_update_readings_and_fetch_responses(self):
        response = self.client.post("/api/devices/readings", json=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Readings updated successfully"})

        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})

        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"latest_timestamp": self.timestamp})

    def test_fetch_counts_for_unknown_device(self):
        response = self.client.get(f"/api/devices/{self.unknown_device_id}/cumulative_count")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": f"Device with id {self.unknown_device_id} not found"})

    def test_fetch_latest_timestamp_for_unknown_device(self):
        response = self.client.get(f"/api/devices/{self.unknown_device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": f"Device with id {self.unknown_device_id} not found"})

    def test_error_message_after_device_capacity_is_reached(self):
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
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Readings updated successfully"})

        response = self.client.post("/api/devices/readings", json=self.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"message": "Capacity exceeded"})

    def test_duplicate_timestamps_in_same_request(self):
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
        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})


    def test_duplicate_timestamps_multiple_requests(self):
        data =  {
            "id": self.device_id,
            "readings": [
                {
                    "timestamp": self.timestamp,
                    "count": 15
                }
            ]
        }

        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 15})

    def test_our_of_order_timestamps(self):
        now = datetime.datetime.now()
        now_string = now.isoformat()
        past_string = (now - datetime.timedelta(seconds=10)).isoformat()
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
        data ["readings"][0]["timestamp"] = past_string
        response = self.client.post("/api/devices/readings", json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"latest_timestamp": now_string})


    def test_multiple_devices(self):
        devices_data = {}
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
            self.assertEqual(response.status_code, 200)

        for device_id, data in devices_data.items():
            response = self.client.get(f"/api/devices/{device_id}/cumulative_count")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"cumulative_count": data["readings"][0]["count"]})

            response = self.client.get(f"/api/devices/{device_id}/latest_timestamp")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"latest_timestamp": data["readings"][0]["timestamp"]})


