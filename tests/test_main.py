import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from dateutil.parser import parse as parse_date


class TestMain(unittest.TestCase):
    """
    Unit tests for the FastAPI application routes.

    The tests use the TestClient class from FastAPI to simulate HTTP requests to the application.
    Input validations tests are included in this class.
    """
    def setUp(self):
        self.client = TestClient(app)
        self.device_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        self.data = {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "readings": [
                {
                    "timestamp": "2024-10-11T02:11:43.862Z",
                    "count": 15
                }
            ]
        }

    @patch('main.device_readings_service')
    def test_update_readings(self, mock_service):
        # Test that the POST /api/devices/readings endpoint returns a success message when readings are added.
        mock_service.add_device_readings.return_value = None
        response = self.client.post("/api/devices/readings", json=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Readings updated successfully"})

    @patch('main.device_readings_service')
    def test_get_cumulative_count(self, mock_service):
        # Test that the GET /api/devices/{device_id}/cumulative_count endpoint returns the correct count.
        mock_service.get_cumulative_count.return_value = (10, None)
        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cumulative_count": 10})

    @patch('main.device_readings_service')
    def test_get_latest_timestamp(self, mock_service):
        # Test that the GET /api/devices/{device_id}/latest_timestamp endpoint returns the correct timestamp.
        dt_string = "2021-09-29T16:08:15+01:00"
        mock_service.get_latest_timestamp.return_value = (parse_date(dt_string), None)
        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"latest_timestamp": dt_string})

    @patch('main.device_readings_service')
    def test_update_readings_error(self, mock_service):
        # Test that the POST /api/devices/readings endpoint returns an error message when an error occurs.
        mock_service.add_device_readings.return_value = "Error message"
        response = self.client.post("/api/devices/readings", json=self.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"message": "Error message"})

    @patch('main.device_readings_service')
    def test_get_cumulative_count_error(self, mock_service):
        # Test that the GET /api/devices/{device_id}/cumulative_count endpoint returns an error message for a missing
        # device.
        mock_service.get_cumulative_count.return_value = (None, "Error message")
        response = self.client.get(f"/api/devices/{self.device_id}/cumulative_count")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Error message"})

    @patch('main.device_readings_service')
    def test_get_latest_timestamp_error(self, mock_service):
        # Test that the GET /api/devices/{device_id}/latest_timestamp endpoint returns an error message for a missing
        # device.
        mock_service.get_latest_timestamp.return_value = (None, "Error message")
        response = self.client.get(f"/api/devices/{self.device_id}/latest_timestamp")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Error message"})

    def test_invalid_uuid(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error for an invalid UUID.
        response = self.client.post("/api/devices/readings", json={
            "id": "invalid-uuid",
            "readings": [
                {"timestamp": "2021-09-29T16:08:15+01:00", "count": 2}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be a valid UUID, invalid character", response.text)

    def test_missing_id(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error when 'id' is missing.
        response = self.client.post("/api/devices/readings", json={
            "readings": [
                {"timestamp": "2021-09-29T16:08:15+01:00", "count": 2}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Field required", response.text)

    def test_invalid_timestamp_format(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error for an invalid timestamp format.
        response = self.client.post("/api/devices/readings", json={
            "id": "36d5658a-6908-479e-887e-a949ec199272",
            "readings": [
                {"timestamp": "2021-09-29-", "count": 2}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be a valid datetime or date, unexpected extra characters at the end of the input",
                      response.text)

    def test_missing_timestamp(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error when 'timestamp' is missing.
        response = self.client.post("/api/devices/readings", json={
            "id": "36d5658a-6908-479e-887e-a949ec199272",
            "readings": [
                {"count": 2}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Field required", response.text)

    def test_invalid_count_type(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error when 'count' is not an integer.
        response = self.client.post("/api/devices/readings", json={
            "id": "36d5658a-6908-479e-887e-a949ec199272",
            "readings": [
                {"timestamp": "2021-09-29T16:08:15+01:00", "count": "two"}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be a valid integer, unable to parse string as an integer", response.text)

    def test_missing_count(self):
        # Test that the POST /api/devices/readings endpoint returns a validation error when 'count' is missing.
        response = self.client.post("/api/devices/readings", json={
            "id": "36d5658a-6908-479e-887e-a949ec199272",
            "readings": [
                {"timestamp": "2021-09-29T16:08:15+01:00"}
            ]
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Field required", response.text)

    def test_empty_readings(self):
        # Test that the POST /api/devices/readings endpoint returns a success message for an empty readings list.
        response = self.client.post("/api/devices/readings", json={
            "id": "36d5658a-6908-479e-887e-a949ec199272",
            "readings": []
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_device_id_in_cumulative_count(self):
        # Test that the GET /api/devices/{device_id}/cumulative_count endpoint returns a validation error for an
        # invalid UUID.
        response = self.client.get("/api/devices/invalid-uuid/cumulative_count")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be a valid UUID, invalid character", response.text)

    def test_invalid_device_id_in_latest_timestamp(self):
        # Test that the GET /api/devices/{device_id}/latest_timestamp endpoint returns a validation error for an
        # invalid UUID.
        response = self.client.get("/api/devices/invalid-uuid/latest_timestamp")
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be a valid UUID, invalid character", response.text)
