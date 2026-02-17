from dataclasses import dataclass
from typing import Iterable, Self

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
        return ArgStack(other.value, self if other.prev is None else self.append_stack(other.prev))

    def __len__(self):
        count = 1
        next = self
        while (next := next.prev):
            count += 1
        return count

    def debug(self) -> Iterable[VIT]:
        yield self.value.tree
        next = self
        while (next := next.prev):
            yield next.value.tree



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
    tree_args: ArgStack | None = None
    simple_args: ArgStack | None = None
    local_context: KeyValueStack | None = None
    outer_context: KeyValueStack | None = None

    def append_tree_arg(self, arg: LazyValue) -> "Context":
        return Context(
            tree_args=ArgStack(arg, self.tree_args),
            simple_args=self.simple_args,
            local_context=self.local_context,
            outer_context=self.outer_context,
        )

    def append_simple_arg(self, arg: LazyValue) -> "Context":
        return Context(
            tree_args=self.tree_args,
            simple_args=ArgStack(arg, self.simple_args),
            local_context=self.local_context,
            outer_context=self.outer_context,
        )

    def append_args(self, tree_args: ArgStack | None, simple_args: ArgStack | None) -> "Context":
        if tree_args is None:
            appended_tree_args = self.tree_args
        elif self.tree_args is None:
            appended_tree_args = tree_args
        else:
            appended_tree_args = self.tree_args.append_stack(tree_args)
        if simple_args is None:
            appended_simple_args = self.simple_args
        elif self.simple_args is None:
            appended_simple_args = simple_args
        else:
            appended_simple_args = self.simple_args.append_stack(simple_args)

        return Context(
            tree_args=appended_tree_args,
            simple_args=appended_simple_args,
            local_context=self.local_context,
            outer_context=self.outer_context,
        )

    def append_local(self, key: bytes, value: LazyValue) -> "Context":
        return Context(
            tree_args=self.tree_args,
            simple_args=self.simple_args,
            local_context=KeyValueStack(value=value, key=key, prev=self.local_context),
            outer_context=self.outer_context,
        )

    def pop_tree_arg(self) -> tuple["Context", ArgStack]:
        if self.tree_args is None:
            raise RuntimeError("TODO arg is None")
        nctx = Context(
            tree_args=self.tree_args.prev,
            simple_args=self.simple_args,
            local_context=self.local_context,
            outer_context=self.outer_context,
        )
        return nctx, self.tree_args

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
