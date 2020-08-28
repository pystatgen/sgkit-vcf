import itertools
import struct
from pathlib import Path
from typing import IO, Any, Iterator, Optional, Sequence, TypeVar

T = TypeVar("T")


def ceildiv(a: int, b: int) -> int:
    """Safe integer ceil function"""
    return -(-a // b)


# https://dev.to/orenovadia/solution-chunked-iterator-python-riddle-3ple
def chunks(iterator: Iterator[T], n: int) -> Iterator[Iterator[T]]:
    """
    Convert an iterator into an iterator of iterators, where the inner iterators
    each return `n` items, except the last, which may return fewer.
    """

    for first in iterator:  # take one item out (exits loop if `iterator` is empty)
        rest_of_chunk = itertools.islice(iterator, 0, n - 1)
        yield itertools.chain([first], rest_of_chunk)  # concatenate the first item back


def get_file_length(path: Path) -> int:
    """Get the length of a file in bytes."""
    return path.stat().st_size


def get_file_offset(vfp: int) -> int:
    """Convert a block compressed virtual file pointer to a file offset."""
    address_mask = 0xFFFFFFFFFFFF
    return vfp >> 16 & address_mask


def read_bytes_as_value(f: IO[Any], fmt: str, nodata: Optional[Any] = None) -> Any:
    """Read bytes using a `struct` format string and return the unpacked data value.

    Parameters
    ----------
    f : IO[Any]
        The IO stream to read bytes from.
    fmt : str
        A Python `struct` format string.
    nodata : Optional[Any], optional
        The value to return in case there is no further data in the stream, by default None

    Returns
    -------
    Any
        The unpacked data value read from the stream.
    """
    data = f.read(struct.calcsize(fmt))
    if not data:
        return nodata
    values = struct.Struct(fmt).unpack(data)
    assert len(values) == 1
    return values[0]


def read_bytes_as_tuple(f: IO[Any], fmt: str) -> Sequence[Any]:
    """Read bytes using a `struct` format string and return the unpacked data values.

    Parameters
    ----------
    f : IO[Any]
        The IO stream to read bytes from.
    fmt : str
        A Python `struct` format string.

    Returns
    -------
    Sequence[Any]
        The unpacked data values read from the stream.
    """
    data = f.read(struct.calcsize(fmt))
    return struct.Struct(fmt).unpack(data)
