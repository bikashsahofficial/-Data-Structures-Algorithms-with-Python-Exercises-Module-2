class ReservedMemory:
    """Simple wrapper around a bytearray to mimic the provided class."""
    def __init__(self, size: int):
        self._data = bytearray(size)

    def copy(self, src: 'ReservedMemory', src_start: int, dst_start: int, length: int) -> None:
        self._data[dst_start:dst_start+length] = src._data[src_start:src_start+length]

    def get_bytes(self, start: int, length: int) -> bytes:
        return bytes(self._data[start:start+length])

    def set_bytes(self, start: int, data: bytes) -> None:
        self._data[start:start+len(data)] = data


class IntArray:
    """Dynamic array storing integers in a ReservedMemory block."""

    def __init__(self, bytes_per_element: int = 2):
        self._element_size = bytes_per_element
        self._size = 0
        self._mem = ReservedMemory(0)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> int:
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        offset = index * self._element_size
        data = self._mem.get_bytes(offset, self._element_size)
        return int.from_bytes(data, 'little', signed=True)

    def __setitem__(self, index: int, value: int) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        self._write_value(self._mem, index, value)

    def __str__(self) -> str:
        elements = [self[i] for i in range(self._size)]
        return f"IntArray ({self._size} elements): {elements}"

    def append(self, value: int) -> None:
        self.insert(self._size, value)

    def insert(self, index: int, value: int) -> None:
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")

        new_mem = ReservedMemory((self._size + 1) * self._element_size)

        if index > 0:
            new_mem.copy(self._mem, 0, 0, index * self._element_size)

        if index < self._size:
            old_offset = index * self._element_size
            new_offset = (index + 1) * self._element_size
            length = (self._size - index) * self._element_size
            new_mem.copy(self._mem, old_offset, new_offset, length)

        self._write_value(new_mem, index, value)

        self._mem = new_mem
        self._size += 1

    def remove(self, index: int) -> int | None:
        if self._size == 0:
            return None
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        removed_value = self[index]

        new_mem = ReservedMemory((self._size - 1) * self._element_size)

        if index > 0:
            new_mem.copy(self._mem, 0, 0, index * self._element_size)

        if index < self._size - 1:
            old_offset = (index + 1) * self._element_size
            new_offset = index * self._element_size
            length = (self._size - index - 1) * self._element_size
            new_mem.copy(self._mem, old_offset, new_offset, length)

        self._mem = new_mem
        self._size -= 1

        return removed_value

    def pop(self) -> int:
        """Remove and return the last element. Raise IndexError if empty."""
        if self._size == 0:
            raise IndexError("pop from empty array")
        return self.remove(self._size - 1)

    def search(self, value: int) -> int:
        """Return the first index where value is found, or -1 if not present."""
        for i in range(self._size):
            if self[i] == value:
                return i
        return -1

    def _write_value(self, mem: ReservedMemory, index: int, value: int) -> None:
        offset = index * self._element_size
        data = value.to_bytes(self._element_size, 'little', signed=True)
        mem.set_bytes(offset, data)