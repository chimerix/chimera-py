from dataclasses import dataclass

from tree_sitter import Node

from chimerix.core import VIT, Context, LazyValue, ctx_debug
from chimerix.ts_helpers import error_format
from chimerix.value import Error, Value


@dataclass
class TreeSitterVIT(VIT):
    node: Node


@dataclass
class VITError(TreeSitterVIT):
    message: str

    def __post_init__(self):
        print(f"VIT ERROR: {self.message}")

    def interpret(self, _: "Context") -> Value:
        return Value(Error(self.message))


@dataclass
class Call(TreeSitterVIT):
    callee: VIT
    argument: VIT

    def interpret(self, ctx: Context) -> Value:
        print(f"{type(self.callee)=}")
        ctx_with_arg = ctx.append_arg(LazyValue(self.argument, ctx))
        print(ctx_debug(ctx_with_arg.local_context))
        return self.callee.interpret(ctx_with_arg)
        # return self.callee.interpret(ctx.append_arg(LazyValue(self.argument, ctx)))


@dataclass
class Variable(TreeSitterVIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        print(f"in variable {id(ctx)=}")
        found = ctx.find_local(self.value)
        if found is None:
            return Value(
                Error(
                    f"variable `{self.value.decode()}` not found"
                    + error_format(self.node)
                )
            )
        return found.tree.interpret(found.context.append_args(ctx.args))


@dataclass
class Int(TreeSitterVIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        try:
            return Value(int(self.value))
        except:
            return Value(Error(f"Error parsing number: `{self.value.decode()}`"))


@dataclass
class Plus(TreeSitterVIT):
    left: VIT
    right: VIT

    def interpret(self, ctx: Context) -> Value:
        left = self.left.interpret(ctx)
        right = self.right.interpret(ctx)
        if isinstance(left.pointer, Error):
            return left
        if isinstance(right.pointer, Error):
            return right
        try:
            return Value(left.pointer + right.pointer)  # type: ignore
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
        if not ctx.args:
            return Value(Error("No args passed"))
        key = self.left.value
        ctx, arg = ctx.pop_arg()
        print(f"arg is: {type(arg.value.tree)}" + error_format(arg.value.tree.node))
        print(f"me is: {type(self)}" + error_format(self.node))
        # print(f"arg and me are same? : {ctx.args.value.tree is self}")
        return arg.value.tree.interpret(
            # ctx.args.value.context.append_local(key, LazyValue(self.right, ctx))
            ctx.append_local(key, LazyValue(self.right, ctx))
        )


@dataclass
class ArgumentPrefix(TreeSitterVIT):
    child: VIT

    def interpret(self, ctx: Context) -> Value:
        value = self.child.interpret(ctx)
        if isinstance(value.pointer, Error):
            print("just hm?")
            return value
        if not isinstance(value.pointer, int):
            return Value(Error(f"`%` child should be int, got `{value.pointer}`"))
        next = ctx.args
        for _ in range(value.pointer):
            if next is None:
                break
            next = next.prev
        if next is None:
            return Value(Error("Arg stack underflor"))
        return next.value.tree.interpret(next.value.context)


@dataclass
class DebugNode(TreeSitterVIT):
    child: VIT

    def interpret(self, ctx: Context) -> Value:
        print("-------")
        print("DEBUG:", ctx_debug(ctx.local_context))
        print("-------")
        return self.child.interpret(ctx)


def pipe(node: Node, group: list[VIT]) -> VIT:
    if len(group) == 0:
        return VIT()
    if len(group) == 1:
        return group[0]
    # return Call(node, pipe(node, group[:-1]), group[-1])
    return Call(node, group[0], pipe(node, group[1:]))


"""
    @pipe
    abra = %0 + %1 ; LazyTree - пустой контекст 
    cadabra = 10 + abra; LazyTree - пустой контекст 

    cadabra: 15: 30

"""
