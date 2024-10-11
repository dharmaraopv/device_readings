import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class Reading(BaseModel):
    timestamp: datetime
    count: int


class DeviceReadings(BaseModel):
    id: uuid.UUID
    readings: List[Reading]
