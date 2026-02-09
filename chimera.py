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
    print("Oh prepare...")
    result = main()
    print("\nWow? Checking...\n")

    if not isinstance(result, core.Value):
        print("what is it?", type(result))
        print("this is:", result)
        sys.exit(1)

    checkError(result, "Not bad, error result is result:")

    if not isinstance(result.pointer, core.Context):
        print(f"{type(result.pointer)=}")
        print(f"{result.pointer=}")
        sys.exit(1)

    result = cast(core.Context, result.pointer)

    print("Nice!")
    find_local = result.find_local(b"result")
    if find_local is None:
        print("Hm, result var not found =(")
        next = result.local_context
        while True:
            if next is None:
                print("|None|")
                break
            print(next.key)
            next = next.prev
        sys.exit(0)
    print("The moment of ...")
    value = find_local.get()
    checkError(value, "Really not bad, error result is result:")
    print("And ...:")
    print(value.pointer)
