from dataclasses import dataclass

from chimerix.core import VIT, Context, KeyValueStack, LazyValue
from chimerix.value import Error, Value

@dataclass
class VITError(VIT):
    message: str

    def interpret(self, _: "Context") -> Value:
        return Value(Error(self.message))

@dataclass
class Call(VIT):
    callee: VIT
    argument: VIT

    def interpret(self, ctx: Context) -> Value:
        return self.callee.interpret(ctx.append_arg(LazyValue(self.argument, ctx)))


@dataclass
class Variable(VIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        found = ctx.find_local(self.value)
        if found is None:
            return Value(Error(f"variable `{self.value.decode()}` not found"))
        return found.tree.interpret(found.context.append_args(ctx.args))


@dataclass
class Int(VIT):
    value: bytes

    def interpret(self, ctx: Context) -> Value:
        try:
            return Value(int(self.value))
        except:
            return Value(Error(f"Error parsing number: `{self.value.decode()}`"))


@dataclass
class Plus(VIT):
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
            return left.pointer + right.pointer  # type: ignore
        except:
            return Value(
                Error(
                    f"Error plusing value: left:`{left.pointer}` right:`{right.pointer}`"
                )
            )


@dataclass
class Assign(VIT):
    left: VIT
    right: VIT

    def interpret(self, ctx: Context) -> Value:
        if not isinstance(self.left, Variable):
            return Value(Error(f"left part of `=` operator should be single identifier, got: {type(VIT)}"))
        variable_name = self.left.value
        return Value(Context(local_context=KeyValueStack(key=variable_name, value=LazyValue(self.right, ctx), prev=None)))

@dataclass
class ArgumentPrefix(VIT):
    child: VIT

    def interpret(self, ctx: Context) -> Value:
        value = self.child.interpret(ctx)
        if isinstance(value.pointer, Error):
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


def pipe(group: list[VIT]) -> VIT:
    if len(group) == 0:
        return VIT()
    if len(group) == 1:
        return group[0]
    return Call(pipe(group[:-1]), group[-1])


"""
    @pipe
    abra = %0 + %1 ; LazyTree - пустой контекст 
    cadabra = 10 + abra; LazyTree - пустой контекст 

    cadabra: 15: 30

"""
