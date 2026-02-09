import abc

from chimerix.core import VIT, Context, LazyValue
from chimerix.value import Error, Value


class Impls(abc.ABC):
    @abc.abstractmethod
    def number(self, value: bytes) -> Value: ...

    @abc.abstractmethod
    def string(self, value: bytes) -> Value: ...

    @abc.abstractmethod
    def plus(self, left: VIT, right: VIT) -> Value: ...

    @abc.abstractmethod
    def assign(self, left: VIT, right: VIT) -> Value: ...


class DefaultImpls(Impls):
    def number(self, value: bytes) -> Value:
        try:
            return Value(int(value))
        except:
            return Value(Error(f"Error parsing number: `{value.decode()}`"))

    def string(self, value: bytes) -> Value:
        return Value(value.decode())

    def plus(self, left: Value, right: Value) -> Value:
        try:
            return left.pointer + right.pointer  # type: ignore
        except:
            return Value(
                Error(
                    f"Error plusing value: left:`{left.pointer}` right:`{right.pointer}`"
                )
            )

    def assign(self, ctx: Context, left: LazyValue, right: LazyValue) -> Value:

        
