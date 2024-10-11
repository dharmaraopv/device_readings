from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    PROJECT_SLUG = "device_readings"
    DEVICE_STORE_CAPACITY: int = 100
    TIMESTAMP_STORE_CAPACITY: int = 10000
