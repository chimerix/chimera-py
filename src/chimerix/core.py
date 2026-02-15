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

    def iter_keys(self):
        next = self
        while True:
            yield next.key
            if next.prev is None:
                break
            next = next.prev


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

    def append_local(self, key: bytes, value: LazyValue) -> "Context":
        return Context(
            args=self.args,
            local_context=KeyValueStack(value=value, key=key, prev=self.local_context),
            outer_context=self.outer_context,
        )

    def pop_arg(self) -> tuple["Context", ArgStack]:
        if self.args is None:
            raise RuntimeError("TODO arg is None")
        nctx = Context(
            args=self.args.prev,
            local_context=self.local_context,
            outer_context=self.outer_context,
        )
        return nctx, self.args

    def find_local(self, variable: bytes) -> LazyValue | None:
        return self._find(variable, self.local_context)

    def find_outer(self, variable: bytes) -> LazyValue | None:
        return self._find(variable, self.outer_context)

    def _find(
        self, variable: bytes, head: KeyValueStack | None
    ) -> LazyValue | None:
        next = head
        while True:
            if next is None:
                print(f"DEBUG: variable not found. State: {ctx_debug(head)}")
                return None
            if next.key == variable:
                return next.value
            next = next.prev

def ctx_debug(head: KeyValueStack | None) -> str:
    joined = b" | ".join(head.iter_keys()) if head else b"<empty>"
    return joined.decode()

def ctx_len(head: KeyValueStack | None) -> int:
    return len(list(head.iter_keys())) if head else 0
