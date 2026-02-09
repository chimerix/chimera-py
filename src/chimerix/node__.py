
# TODO TODO TODO TODO
# TODO TODO TODO TODO
# TODO TODO TODO TODO
# TODO TODO TODO TODO

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, final

# @dataclass
# class Value:
#     is_error: bool
#     value: Any

# class Dangle(ABC):
#     @abstractmethod
#     def get(self, args: list[Any]) -> Value:
#         ...


# @dataclass
# class Error:
#     message: str

# @dataclass
# class ErrorValue(Value):
#     error: Error
    

# @dataclass
# class Node(ABC):
#     applied: bool = False

#     @abstractmethod
#     def apply_internal(self, ctx: Context) -> Value:
#         ...

#     @final
#     def apply_safe(self, ctx: Context) -> Value:
#         if self.applied:
#             return 
#         return self.apply(ctx)
