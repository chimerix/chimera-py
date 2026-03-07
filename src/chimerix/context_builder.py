from dataclasses import dataclass, field
from typing import Callable

from chimerix.core import Context, KeyValueStack, LazyValue
from chimerix.vit_nodes import CustomFunc, CustomFuncType


@dataclass
class ContextBuilder:
    funcs: list[tuple[str, CustomFuncType]] = field(default_factory=list)

    def register_outer(self, func_name: str) -> Callable:
        def decorator(func: CustomFuncType):
            self.funcs.append((func_name, func))

        return decorator

    def build_context(self) -> Context:
        outer_context = None
        for func_name, func in self.funcs:
            new_outer_context = KeyValueStack(
                prev = outer_context,
                key = func_name.encode(),
                value=LazyValue(
                    context=Context(),
                    tree=CustomFunc(func)
                ),
            )
            outer_context = new_outer_context
        return Context(
            tree_args=None,
            simple_args=None,
            local_context=None,
            outer_context=outer_context,
        )
