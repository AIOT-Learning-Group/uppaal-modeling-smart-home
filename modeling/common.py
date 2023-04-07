from typing import Callable, Tuple, Union
from typing_extensions import TypeAlias

Name: TypeAlias = str
Tplt: TypeAlias = str
Decl: TypeAlias = str
Inst: TypeAlias = str
Sys: TypeAlias = str
Var: TypeAlias = str
PartialComposition = Tuple[Name, Tplt, Decl]
Composition = Tuple[Tplt, Decl, Inst, Sys, Var]
PartialTemplateGenerator = Callable[[int], PartialComposition]
TemplateGenerator = Callable[[int], Composition]


class ComposableTemplate:
    def __init__(self, template_generator: PartialTemplateGenerator, used_nodes: int):
        self.generator = template_generator
        self.used_nodes = used_nodes

    def compose(self, starting_node_id: int, instance_number: Union[None, int] = None) -> Composition:
        [name, tplt, decl] = self.generator(starting_node_id)
        inst = ""
        sys = ""
        var = ""
        if "{number}" in decl and type(instance_number) == int:
            decl = decl.format(number=instance_number)
            for i in range(instance_number):
                inst += f"{name}{i}={name}({i});"
                sys += f",{name}{i}"
                var += f",{name.lower()}[{i}]"
        else:
            sys = f",{name}"
            var = f",{name.lower()}"
        return tplt, decl, inst, sys, var
