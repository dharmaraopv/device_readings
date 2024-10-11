import uuid
from fastapi import FastAPI, Response, status
from device_readings_service import device_readings_service
from models import DeviceReadings

app = FastAPI()


@app.post("/api/devices/readings")
def update_readings(readings: DeviceReadings, response: Response):
    """
    Endpoint to add or update readings for a device.

    This endpoint takes a JSON payload containing device readings and updates the store accordingly.
    If there is an issue with adding the readings, it returns a 500 Internal Server Error.


    Args:
        readings (DeviceReadings): The readings data containing the device ID and associated readings.
        response (Response): The response object for setting the status code.

    Example JSON payload:
    {
        "id": "6e7b58d7-0e4f-4b6c-8b9a-0b9f9b9c9d6f",
        "readings": [
            {
                "timestamp": "2021-09-30T12:00:00",
                "count": 5
            },
            {
                "timestamp": "2021-09-30T12:05:00",
                "count": 3
            }
        ]
    }

    Returns:
        dict: A success message or an error message with 500 status if the update fails.
    """
    err = device_readings_service.add_device_readings(readings)
    if err:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": err}
    return {"message": "Readings updated successfully"}


@app.get("/api/devices/{device_id}/cumulative_count")
def get_cumulative_count(device_id: uuid.UUID, response: Response):
    """
    Endpoint to retrieve the cumulative count of readings for a specified device.

    This endpoint returns the total count of all readings recorded for a device identified by `device_id`.
    If the device is not found, it returns a 404 Not Found status.

    Args:
        device_id (uuid.UUID): The unique identifier of the device.
        response (Response): The response object for setting the status code.

    Returns:
        dict: A JSON object with the cumulative count or an error message if the device is not found.
    """
    count, err = device_readings_service.get_cumulative_count(device_id)
    if err:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": err}
    return {"cumulative_count": count}


@app.get("/api/devices/{device_id}/latest_timestamp")
def get_latest_timestamp(device_id: uuid.UUID, response: Response):
    """
    Endpoint to retrieve the latest timestamp of readings for a specified device.

    This endpoint returns the most recent timestamp recorded for a device identified by `device_id`.
    If the device is not found, it returns a 404 Not Found status.

    Args:
        device_id (uuid.UUID): The unique identifier of the device.
        response (Response): The response object for setting the status code.

    Returns:
        dict: A JSON object with the latest timestamp or an error message if the device is not found.
    """
    timestamp, err = device_readings_service.get_latest_timestamp(device_id)
    if err:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": err}
    return {"latest_timestamp": timestamp}
