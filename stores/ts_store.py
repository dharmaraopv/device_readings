import uuid
from abc import ABC, abstractmethod


class TimeStampStore(ABC):
    @abstractmethod
    def check_and_add_timestamp(self, device_id: uuid.UUID, timestamp: int) -> bool:
        """
        # Check if the timestamp is already present in the store.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """
        # Clear the store.
        """
        pass
