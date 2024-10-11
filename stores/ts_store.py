import uuid
from abc import ABC, abstractmethod


class TimeStampStoreIface(ABC):
    """
    Abstract interface for a timestamp store, which manages timestamps for various devices.

    This interface defines the basic operations for adding and checking timestamps as well as
    clearing the store.
    """

    @abstractmethod
    def check_and_add_timestamp(self, device_id: uuid.UUID, timestamp: int) -> bool:
        """
        Check if a timestamp for a specific device is present in the store and add it if not.

        This method should check whether the specified timestamp is already associated with the given
        device in the store. If it is not present, the timestamp should be added to the store.

        Args:
            device_id (uuid.UUID): The unique identifier of the device.
            timestamp (int): The timestamp to check, in Unix epoch format.

        Returns:
            bool: True if the timestamp was added (i.e., it was not already present), False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """
        Clear all entries from the store.

        This method should reset the store, removing all stored timestamps and returning it to
        an empty state.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass
