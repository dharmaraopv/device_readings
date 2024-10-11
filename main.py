import uuid

from fastapi import FastAPI, Path, Response, status
from device_readings_service import device_readings_service
from models import DeviceReadings

app = FastAPI()


@app.post("/api/devices/readings")
def update_readings(readings: DeviceReadings, response: Response):
    err = device_readings_service.add_device_readings(readings)
    if err:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": err}
    return {"message": "Readings updated successfully"}


@app.get("/api/devices/{device_id}/cumulative_count")
def get_culumative_count(device_id: uuid.UUID, response: Response):
    count, err = device_readings_service.get_cumulative_count(device_id)
    if err:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": err}
    return {"cumulative_count": count}

@app.get("/api/devices/{device_id}/latest_timestamp")
def get_latest_timestamp(device_id: uuid.UUID, response: Response):
    timestamp, err = device_readings_service.get_latest_timestamp(device_id)
    if err:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": err}
    return {"latest_timestamp": timestamp}
