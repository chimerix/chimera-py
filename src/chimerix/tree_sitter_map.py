import enum
import functools

from tree_sitter import Language, Node, Parser
from tree_sitter_chimera import language

import chimerix.vit_nodes as vit
from chimerix.core import VIT

TS_CHIMERA = Language(language())
parser = Parser(TS_CHIMERA)


class TreeSitterTypes(enum.StrEnum):
    source_file = "source_file"
    binary_expression = "binary_expression"
    const_value = "const_value"
    const_string = "const_string"
    const_number = "const_number"
    function_call_list = "function_call_list"
    list_pattern = "list_pattern"


def _child_n(node: Node, n: int) -> Node:
    child = node.child(n)
    if child is None:
        raise TypeError(f"Node {node.type} does not have children")
    return child


_child_0 = functools.partial(_child_n, n=0)
_child_1 = functools.partial(_child_n, n=1)
_child_2 = functools.partial(_child_n, n=2)


def to_vit(node: Node) -> VIT:
    match (node.type):
        case TreeSitterTypes.source_file:
            return vit.pipe(list(map(to_vit, node.children)))
        case TreeSitterTypes.const_value:
            return to_vit(_child_0(node))
        case TreeSitterTypes.const_number:
            return vit.Int(node.text or b"???")
        case TreeSitterTypes.binary_expression:
            left = _child_0(node)
            operator = _child_1(node)
            right = _child_2(node)
            match operator.text:
                case b"+":
                    return vit.Plus(
                        left=to_vit(left),
                        right=to_vit(right),
                    )
                # case b".":
                #     return CallOp(
                #         left=to_interpreter_tree(left),
                #         right=ContextIdentifier(to_interpreter_tree(right)),
                #     )
                case b"=":
                    return vit.Assign(
                        left=to_vit(left),
                        right=to_vit(right),
                    )
                case b":" | b"::":
                    return vit.Call(
                        callee=to_vit(left),
                        argument=to_vit(right),
                    )
                case _:
                    return vit.VITError(f"Unknown Binary Operation {node.text}")
        case other:
            return vit.VITError(f"Node unsupported yet: {other}")
