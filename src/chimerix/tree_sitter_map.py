import enum
import functools
import itertools
from typing import Iterable

from tree_sitter import Language, Node, Parser
from tree_sitter_chimera import language

import chimerix.vit_nodes as vit
from chimerix.core import VIT

TS_CHIMERA = Language(language())
parser = Parser(TS_CHIMERA)


class TreeSitterTypes(enum.StrEnum):
    source_file = "source_file"
    binary_expression = "binary_expression"
    unary_expression = "unary_expression"
    const_value = "const_value"
    const_string = "const_string"
    const_number = "const_number"
    function_call_list = "function_call_list"
    # list_pattern = "list_pattern"
    identifier = "identifier"
    group = "group"
    comment = "comment"

def skip_comments(children: Iterable[Node]) -> Iterable[Node]:
    return filter(lambda x: x.type != TreeSitterTypes.comment,  children)

def _child_n(node: Node, n: int) -> Node:
    try:
        return next(itertools.islice(skip_comments(node.children), n, None))
    except StopIteration:
        raise TypeError(f"Node {node.type} does not have {n}-nth children")


_child_0 = functools.partial(_child_n, n=0)
_child_1 = functools.partial(_child_n, n=1)
_child_2 = functools.partial(_child_n, n=2)


def to_vit(node: Node) -> VIT:
    match (node.type):
        case TreeSitterTypes.source_file:
            return vit.pipe(node, list(map(to_vit, skip_comments(node.children))))
        case TreeSitterTypes.const_value:
            return to_vit(_child_0(node))
        case TreeSitterTypes.const_number:
            return vit.Int(node, node.text or b"???")
        case TreeSitterTypes.binary_expression:
            left = _child_0(node)
            operator = _child_1(node)
            right = _child_2(node)
            match operator.text:
                case b"+":
                    return vit.PyOperator(
                        node,
                        left=to_vit(left),
                        right=to_vit(right),
                        operator="__add__",
                    )
                case b"-":
                    return vit.PyOperator(
                        node,
                        left=to_vit(left),
                        right=to_vit(right),
                        operator="__sub__",
                    )
                case b"*":
                    return vit.PyOperator(
                        node,
                        left=to_vit(left),
                        right=to_vit(right),
                        operator="__mul__",
                    )
                case b"/":
                    return vit.PyOperator(
                        node,
                        left=to_vit(left),
                        right=to_vit(right),
                        operator="__truediv__",
                    )
                # case b".":
                #     return CallOp(
                #         left=to_interpreter_tree(left),
                #         right=ContextIdentifier(to_interpreter_tree(right)),
                #     )
                case b"=":
                    return vit.Assign(
                        node,
                        left=to_vit(left),
                        right=to_vit(right),
                    )
                case b":" | b"::" | b".":
                    return vit.Call(
                        node,
                        callee=to_vit(left),
                        argument=to_vit(right),
                    )
                case b"|":
                    return vit.Call(
                        node,
                        callee=to_vit(right),
                        argument=to_vit(left),
                    )
                case _:
                    return vit.VITError(node, f"Unknown Binary Operation {node.text}")
        case TreeSitterTypes.unary_expression:
            operator = _child_0(node)
            argument = _child_1(node)
            match operator.text:
                case b"%":
                    return vit.ArgumentPrefix(node, to_vit(argument))
                case b"$":
                    return vit.DebugNode(node, to_vit(argument))
                case _:
                    return vit.VITError(node, f"Unknown Unary Operation {node.text}")
        case TreeSitterTypes.identifier:
            return vit.Variable(node, node.text or b"???")
        case TreeSitterTypes.group:
            if node.child_count < 3:
                # vit.VITError(node, f"Only group with one child supported currently, but got: {node.child_count - 2}")
                return vit.VITError(node, f"Group should contain at least 1 child, got: {node.child_count - 2}")
            # skip_comments(node.children[1:-1])
            # return to_vit(_child_1(node))
            return vit.pipe(node, list(map(to_vit, skip_comments(node.children[1:-1]))))
        case other:
            return vit.VITError(node, f"Node unsupported yet: {other}")
