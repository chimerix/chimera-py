from dataclasses import dataclass

from tree_sitter import Node

from chimerix.core import VIT, ArgStack, Context, LazyValue
from chimerix.ts_helpers import error_format
from chimerix.value import Error, Value

log = print  # TODO


class LoggingMeta(type):
    def __new__(cls, name, bases, attrs):
        if "interpret" in attrs:
            original_interpret = attrs["interpret"]

            def wrapped_interpret(self, ctx):
                log(f">>> {type(self).__name__}", error_format(self.node))
                return original_interpret(self, ctx)

            attrs["interpret"] = wrapped_interpret
        return super().__new__(cls, name, bases, attrs)


@dataclass
class TreeSitterVIT(VIT, metaclass=LoggingMeta):
    node: Node


@dataclass
class VITError(TreeSitterVIT):
    message: str

    def __post_init__(self):
        log(f"VIT ERROR: {self.message}")

    def interpret(self, _: "Context") -> Value:
        return Value(Error(self.message))


@dataclass
class TreeCall(TreeSitterVIT):
    callee: VIT
    argument: VIT

    def interpret(self, ctx: Context) -> Value:
        ctx_with_tree_arg = ctx.append_tree_arg(LazyValue(self.argument, ctx))
        return self.callee.interpret(ctx_with_tree_arg)


@dataclass
class DotCall(TreeSitterVIT):
    callee: VIT
    argument: VIT

    def interpret(self, ctx: Context) -> Value:
        return self.callee.interpret(
            Context(
                tree_args=ArgStack(LazyValue(self.argument, ctx), ctx.tree_args),
                simple_args=None,
                local_context=ctx.local_context,
                outer_context=ctx.outer_context,
            )
        )


@dataclass
class ArgCall(TreeSitterVIT):
    callee: VIT
    argument: VIT

    def interpret(self, ctx: Context) -> Value:
        ctx_with_arg = ctx.append_simple_arg(LazyValue(self.argument, ctx))
        return self.callee.interpret(ctx_with_arg)


@dataclass
class Variable(TreeSitterVIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        found = ctx.find_local(self.value)
        if found is None:
            return Value(
                Error(
                    f"variable `{self.value.decode()}` not found"
                    + error_format(self.node)
                )
            )

        return found.tree.interpret(
            found.context.append_args(ctx.tree_args, ctx.simple_args)
        )


@dataclass
class Int(TreeSitterVIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        _ = ctx
        try:
            return Value(int(self.value))
        except:
            return Value(Error(f"Error parsing number: `{self.value.decode()}`"))


@dataclass
class String(TreeSitterVIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        _ = ctx
        try:
            return Value(str(self.value))
        except:
            return Value(Error(f"Error parsing number: `{self.value.decode()}`"))


@dataclass
class PyOperator(TreeSitterVIT):
    left: VIT
    right: VIT
    operator: str

    def interpret(self, ctx: Context) -> Value:
        left = self.left.interpret(ctx)
        right = self.right.interpret(ctx)
        if isinstance(left.pointer, Error):
            return left
        if isinstance(right.pointer, Error):
            return right
        try:
            return Value(getattr(left.pointer, self.operator)(right.pointer))  # type: ignore
        except:
            return Value(
                Error(
                    f"Error plusing value: left:`{left.pointer}` right:`{right.pointer}`"
                )
            )


@dataclass
class Assign(TreeSitterVIT):
    left: VIT
    right: VIT

    def interpret(self, ctx: Context) -> Value:
        if not isinstance(self.left, Variable):
            return Value(
                Error(
                    f"left part of `=` operator should be single identifier, got: {type(self.left)}"
                )
            )
        if not ctx.tree_args:
            return Value(Error("No args passed"))
        key = self.left.value
        ctx, arg = ctx.pop_tree_arg()
        return arg.value.tree.interpret(
            ctx.append_local(key, LazyValue(self.right, ctx))
        )


@dataclass
class ArgumentPrefix(TreeSitterVIT):
    child: VIT

    def interpret(self, ctx: Context) -> Value:
        value = self.child.interpret(ctx)
        if isinstance(value.pointer, Error):
            return value
        if not isinstance(value.pointer, int):
            return Value(Error(f"`%` child should be int, got `{value.pointer}`"))
        next = ctx.simple_args
        for _ in range(value.pointer):
            if next is None:
                break
            next = next.prev
        if next is None:
            return Value(Error("Arg stack underfloor").update(self.node))
        return next.value.tree.interpret(next.value.context)


@dataclass
class DebugNode(TreeSitterVIT):
    child: VIT

    def interpret(self, ctx: Context) -> Value:
        import rich

        rich.print("-------<")
        log("DEGUG", error_format(self.node))
        list(map(rich.print ,(ctx.simple_args.debug() if ctx.simple_args else ())))
        rich.print(">-------")
        return self.child.interpret(ctx)


def pipe(node: Node, group: list[VIT]) -> VIT:
    if len(group) == 0:
        return VIT()
    if len(group) == 1:
        return group[0]
    return TreeCall(node, group[0], pipe(node, group[1:]))
