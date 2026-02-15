import sys
from typing import cast

import chimerix.core as core
import chimerix.tree_sitter_map as chi_ts
from chimerix.value import Value

ctx = core.Context()


def main():
    if len(sys.argv) < 2:
        print("Usage: python chimera.py <path_to_file>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        return chi_ts.to_vit(chi_ts.parser.parse(f.read()).root_node).interpret(ctx)


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
