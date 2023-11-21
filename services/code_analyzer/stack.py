from typing import Any, List


class Stack:

    _stack: List[Any]

    def __init__(self):
        self._stack = []

    def push(self, item: Any):
        self._stack.append(item)

    def pop(self) -> Any:
        return self._stack.pop()

    def peek(self) -> Any:
        return self._stack[-1]

    def __len__(self) -> int:
        return len(self._stack)
