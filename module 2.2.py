class ReservedMemory:
    """Simple wrapper around a bytearray to mimic the provided class."""
    def __init__(self, size: int):
        self._data = bytearray(size)

    def copy(self, src: 'ReservedMemory', src_start: int, dst_start: int, length: int) -> None:
        """Copy a slice from another ReservedMemory into this one."""
        self._data[dst_start:dst_start+length] = src._data[src_start:src_start+length]

    def get_bytes(self, start: int, length: int) -> bytes:
        """Retrieve a slice of bytes."""
        return bytes(self._data[start:start+length])

    def set_bytes(self, start: int, data: bytes) -> None:
        """Store a bytes object at the given offset."""
        self._data[start:start+len(data)] = data


class IntArray:
    """Dynamic array storing integers in a ReservedMemory block."""

    def __init__(self, bytes_per_element: int = 2):
        """Initialize an empty array."""
        self._element_size = bytes_per_element
        self._size = 0
        self._mem = ReservedMemory(0)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> int:
        """Return the integer at the given index."""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        offset = index * self._element_size
        data = self._mem.get_bytes(offset, self._element_size)
        return int.from_bytes(data, 'little', signed=True)

    def __setitem__(self, index: int, value: int) -> None:
        """Set the integer at the given index."""
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        self._write_value(self._mem, index, value)

    def __str__(self) -> str:
        """Return a string representation in the expected format."""
        elements = [self[i] for i in range(self._size)]
        return f"IntArray ({self._size} elements): {elements}"

    def append(self, value: int) -> None:
        """Add a value at the end of the array."""
        self.insert(self._size, value)

    def insert(self, index: int, value: int) -> None:
        """
        Insert a new element at the given index.
        Raises IndexError if index is out of bounds.
        """
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")

        # Create a new memory block for size+1 elements
        new_mem = ReservedMemory((self._size + 1) * self._element_size)

        # Copy elements before the insertion point
        if index > 0:
            new_mem.copy(self._mem, 0, 0, index * self._element_size)

        # Copy elements after the insertion point, shifting them right by one slot
        if index < self._size:
            old_offset = index * self._element_size
            new_offset = (index + 1) * self._element_size
            length = (self._size - index) * self._element_size
            new_mem.copy(self._mem, old_offset, new_offset, length)

        # Write the new value at the target index
        self._write_value(new_mem, index, value)

        # Replace the old memory and update size
        self._mem = new_mem
        self._size += 1

    def remove(self, index: int) -> int | None:
        """
        Remove and return the element at the given index.
        Return None if the array is empty.
        Raise IndexError if index is out of bounds.
        """
        if self._size == 0:
            return None

        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        # Save the value to be returned
        removed_value = self[index]

        # Create a new memory block for size-1 elements
        new_mem = ReservedMemory((self._size - 1) * self._element_size)

        # Copy elements before the removal point
        if index > 0:
            new_mem.copy(self._mem, 0, 0, index * self._element_size)

        # Copy elements after the removal point, shifting them left
        if index < self._size - 1:
            old_offset = (index + 1) * self._element_size
            new_offset = index * self._element_size
            length = (self._size - index - 1) * self._element_size
            new_mem.copy(self._mem, old_offset, new_offset, length)

        # Replace the memory and update size
        self._mem = new_mem
        self._size -= 1

        return removed_value

    def _write_value(self, mem: ReservedMemory, index: int, value: int) -> None:
        """Store an integer into the memory block at the given index."""
        offset = index * self._element_size
        data = value.to_bytes(self._element_size, 'little', signed=True)
        mem.set_bytes(offset, data)