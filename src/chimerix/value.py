from dataclasses import dataclass
from typing import Any
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


@dataclass
class Value:
    pointer: Error | int | str | Any
    _type: None = None  # for usage in future self-hosted interpreter

    # @classmethod
    # def error(cls, pointer, msg) -> Self:
    #     return cls(
    #         type=ValueTypes.Error,
    #         pointer=Error(
    #             range=
    #         ),
    #     )
        

