import enum

import tree_sitter_chimera as tschimera
from tree_sitter import Language, Parser

parser = Parser(Language(tschimera.language()))


class TreeSitterTypes(enum.StrEnum):
    identifier = "identifier"
    path = "path"
    binnary_expression = "binnary_expression"
    unary_expression = "unary_expression"
    const_value = "const_value"
    list = "list"
    curly_list = "curly_list"
    pipe = "pipe"
    group = "group"

