import sys

import chimerix.core as core
import chimerix.tree_sitter_map as chi_ts
from chimerix.context_builder import ContextBuilder
from chimerix.value import Error, Value

builder = ContextBuilder()


@builder.register_outer("len")
def len_(ctx: core.Context) -> Value:
    arg = ctx.simple_args
    if arg is None:
        return Value(Error("No args provided for `@len` function"))
    value = arg.value.get()
    if isinstance(value.pointer, Error):
        return value
    try:
        return Value(len(value.pointer))  # type: ignore
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Тип исключения:", exc_type)
        print("Значение исключения:", exc_value)
        print("Объект traceback:", exc_traceback)
    return Value(Error("got exception in @len func"))


@builder.register_outer("e")
def escaper(ctx: core.Context) -> Value:
    ctx, arg = ctx.pop_tree_arg()
    return arg.value.tree.interpret(core.Context(None, None, None, ctx.local_context))


# ctx = builder.build_context()
# next_ = ctx.outer_context
# while next_:
#     print("***", next_)
#     next_ = next_.prev
# print("***", "END")


def main():
    if len(sys.argv) < 2:
        print("Usage: python chimera.py <path_to_file>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        return chi_ts.to_vit(chi_ts.parser.parse(f.read()).root_node).interpret(
            builder.build_context()
        )


# ls = chimerix.LanguageServer(ctx, main)


def checkError(maybe_error: Value, message: str):
    if isinstance(maybe_error.pointer, core.Error):
        print(message)
        print(maybe_error.pointer.message)
        sys.exit(0)


if __name__ == "__main__":
    print("Preparing...")
    result = main()
    print("\nExexcution Succeed\n")

    if not isinstance(result, core.Value):
        print("what is it?", type(result))
        print("this is:", result)
        sys.exit(1)

    checkError(result, "Got Error:")

    print(f"result type: {type(result.pointer)}")
    print(result.pointer)
