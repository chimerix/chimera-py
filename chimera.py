import sys

import chimerix.core as core
import chimerix.tree_sitter_map as chi_ts

ctx = core.Context()


def main():
    with open("example/main.chi", "rb") as f:
        return chi_ts.to_vit(chi_ts.parser.parse(f.read()).root_node).interpret(ctx)


# ls = chimerix.LanguageServer(ctx, main)


if __name__ == "__main__":
    print("Oh prepare...")
    result = main()
    print("Wow? Checking...")

    if isinstance(result, core.Error):
        print("Not bad, error result is result:")
        print(result.message)
        sys.exit(0)

    if not isinstance(result, core.Context):
        print("what it is?", type(result))
        sys.exit(1)

    print("Nice!")
    find_local = result.find_local(b"result")
    if find_local is None:
        print("Hm, result var not found =(")
        sys.exit(0)
    print("The moment of ...")
    value = find_local.get()
    if isinstance(result, core.Error):
        print("Really not bad, error result is result:")
        print(result.message)
        sys.exit(0)
    print("And ...:")
    print(value.pointer)
