from dataclasses import dataclass
from typing import Self

from chimerix.value import Error, Value


class VIT:
    "Virtual Interpreter Tree"

    def interpret(self, ctx: "Context") -> Value:
        return Value(Error("Uninitialized VIT"))


@dataclass
class LazyValue:
    tree: VIT
    context: "Context"

    def get(self) -> Value:
        return self.tree.interpret(self.context)


@dataclass
class ArgStack:
    value: LazyValue
    prev: Self | None

    def append_stack(self, other: Self) -> "ArgStack":
        if other.prev is None:
            return ArgStack(other.value, self)
        return self.append_stack(other.prev)


@dataclass
class KeyValueStack(ArgStack):
    key: bytes





@dataclass
class Context:
    args: ArgStack | None = None
    local_context: KeyValueStack | None = None
    outer_context: KeyValueStack | None = None

    def append_arg(self, arg: LazyValue) -> "Context":
        return Context(
            args=ArgStack(arg, self.args),
            local_context=self.local_context,
            outer_context=self.outer_context,
        )

    def append_args(self, args: ArgStack | None) -> "Context":
        if args is None:
            return self
        if self.args is None:
            appended = args
        else:
            appended = self.args.append_stack(args)
        return Context(
            args=appended,
            local_context=self.local_context,
            outer_context=self.outer_context,
        )

    def find_local(self, variable: bytes) -> LazyValue | None:
        return self._find_general(variable, self.local_context)

    def find_outer(self, variable: bytes) -> LazyValue | None:
        return self._find_general(variable, self.outer_context)

    def _find_general(
        self, variable: bytes, head: KeyValueStack | None
    ) -> LazyValue | None:
        next = head
        while True:
            if next is None:
                return None
            if next.key == variable:
                return next.value
            next = next.prev
