import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel


class Reading(BaseModel):
    """
    Model representing a single reading for a device.

    Attributes:
        timestamp (datetime): The datetime when the reading was recorded.
        count (int): The count associated with this reading.
    """
    timestamp: datetime
    count: int


class DeviceReadings(BaseModel):
    """
    Model representing a collection of readings for a specific device.

    Attributes:
        id (uuid.UUID): The unique identifier of the device.
        readings (List[Reading]): A list of readings associated with the device.
    """
    id: uuid.UUID
    readings: List[Reading]