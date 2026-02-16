from dataclasses import dataclass
from typing import Any

from chimerix.ts_helpers import error_format
from tree_sitter import Node
# import enum
# from typing import Any, Self


# class ValueTypes(enum.Enum):
#     Error = enum.auto()
#     Int = enum.auto()
#     Str = enum.auto()

@dataclass
class Error:
    message: str
    filename: str = ""
    range: tuple[int, int] = (0, 0)

    def update(self, node: Node) -> "Error":
        self.message = f"{self.message}\n{error_format(node)}"
        return self

@dataclass
class Value:
    pointer: Error | int | str | Any
    _type: None = None  # for usage in future self-hosted interpreter

    # def __add__(self, other) -> Value:
    #     return Value()

    # @classmethod
    # def error(cls, pointer, msg) -> Self:
    #     return cls(
    #         type=ValueTypes.Error,
    #         pointer=Error(
    #             range=
    #         ),
    #     )
        

