from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from typing import Optional

from hub.constants import BYTE_PADDING
from hub.util.assert_byte_indexes import assert_byte_indexes


class StorageProvider(ABC, MutableMapping):
    """An abstract base class for implementing a storage provider.

    To add a new provider using Provider, create a subclass and implement all 5 abstract methods below.
    """

    @abstractmethod
    def __getitem__(self, path: str):
        """Gets the object present at the path within the given byte range.

        Args:
            path (str): The path relative to the root of the provider.

        Returns:
            bytes: The bytes of the object present at the path.

        Raises:
            KeyError: If an object is not found at the path.
        """

    def get_bytes(
        self,
        path: str,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ):
        """Gets the object present at the path within the given byte range.

        Args:
            path (str): The path relative to the root of the provider.
            start_byte (int, optional): If only specific bytes starting from start_byte are required.
            end_byte (int, optional): If only specific bytes up to end_byte are required.

        Returns:
            bytes: The bytes of the object present at the path within the given byte range.

        Raises:
            InvalidBytesRequestedError: If `start_byte` > `end_byte` or `start_byte` < 0 or `end_byte` < 0.
            KeyError: If an object is not found at the path.
        """
        assert_byte_indexes(start_byte, end_byte)
        return self[path][start_byte:end_byte]

    @abstractmethod
    def __setitem__(self, path: str, value: bytes):
        """Sets the object present at the path with the value

        Args:
            path (str): the path relative to the root of the provider.
            value (bytes): the value to be assigned at the path.
        """

    def set_bytes(
        self,
        path: str,
        value: bytes,
        start_byte: Optional[int] = None,
        overwrite: Optional[bool] = False,
    ):
        """Sets the object present at the path with the value

        Args:
            path (str): the path relative to the root of the provider.
            value (bytes): the value to be assigned at the path.
            start_byte (int, optional): If only specific bytes starting from start_byte are to be assigned.
            overwrite (boolean, optional): If the value is True, if there is an object present at the path
                it is completely overwritten, without fetching it's data.

        Raises:
            InvalidBytesRequestedError: If `start_byte` < 0.
        """
        start_byte = start_byte or 0
        end_byte = start_byte + len(value)
        assert_byte_indexes(start_byte, end_byte)

        if path in self and not overwrite:
            current_value = bytearray(self[path])
            # need to pad with zeros at the end to write extra bytes
            if end_byte > len(current_value):
                current_value = current_value.ljust(end_byte, BYTE_PADDING)
            current_value[start_byte:end_byte] = value
            self[path] = current_value
        else:
            # need to pad with zeros at the start to write from an offset
            if start_byte != 0:
                value = value.rjust(end_byte, BYTE_PADDING)
            self[path] = value

    @abstractmethod
    def __iter__(self):
        """Generator function that iterates over the keys of the provider.

        Yields:
            str: the path of the object that it is iterating over, relative to the root of the provider.
        """

    @abstractmethod
    def __delitem__(self, path: str):
        """Delete the object present at the path.

        Args:
            path (str): the path to the object relative to the root of the provider.

        Raises:
            KeyError: If an object is not found at the path.
        """

    @abstractmethod
    def __len__(self):
        """Returns the number of files present inside the root of the provider.

        Returns:
            int: the number of files present inside the root.
        """

    def flush(self):
        """Only needs to be implemented for caches. Flushes the data to the next storage provider.
        Should be a no op for Base Storage Providers like local, s3, azure, gcs, etc.
        """