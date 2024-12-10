from dataclasses import dataclass
from io import BytesIO
from typing import Any, Optional, Self


@dataclass
class Result:
    """Represents the outcome of an operation with optional value and error information.

    This class should be instantiated using the static methods:

        >>> Result.ok(stream, "my val")
        >>> Result.err(stream, "my error message")
    """

    status: bool
    stream: BytesIO
    value: Optional[Any]
    error_msg: Optional[str] = None

    @staticmethod
    def ok(stream: BytesIO, value: Any) -> "Result":
        """Creates a Result representing a successful operation."""
        return Result(True, stream, value, None)

    @staticmethod
    def err(
        stream: BytesIO,
        error_msg: Optional[str] = None,
    ) -> "Result":
        """Creates a Result representing a failed operation with an optional error message."""
        error_location = stream.tell()
        return Result(
            False,
            stream,
            None,
            error_msg if error_msg else f"Error at byte position {error_location}",
        )

    def is_ok(self) -> bool:
        return self.status

    def is_err(self) -> bool:
        return not self.status

    def unwrap(self) -> Any:
        """Return the value if the result is Ok, otherwise raise an exception."""
        if self.is_ok():
            return self.value
        raise ValueError("Called unwrap on an Err value")

    def unwrap_or(self, default: Any) -> Any:
        """Return the value if Ok, otherwise return the provided default value."""
        if self.is_err():
            return default
        return self.value

    def expect(self, err_msg: str) -> Any:
        """Return the value if Ok, otherwise raise an exception with a custom message."""
        if self.is_err():
            raise ValueError(f"{err_msg}: {self.error_msg}")
        return self.value

    def aggregate(self, other: Self | None = None):
        """Aggregate the current result with another result."""
        if not other:
            return self

        if self.is_err() and other.is_err():
            combined_error = f"{self.error_msg} -> {other.error_msg}" if self.error_msg else other.error_msg
            return Result.err(self.stream, error_msg=combined_error)

        if isinstance(self.value, dict) and isinstance(other.value, dict):
            merged_value = {**self.value, **other.value}
        if isinstance(other.value, list):
            other.value.append(self.value)
            merged_value = other.value
        else:
            merged_value = self.value + other.value
        # Aggregate the values while keeping the updated stream position
        return Result.ok(other.stream, merged_value)

    def __bool__(self):
        return self.is_ok()

    def __str__(self):
        return f"Result(status={self.status}, value={self.value}, error={self.error_msg})"
