_base = f"Usage: python {__file__}"


class ParamItem:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc


class Param:
    def __init__(self, command_name: str, description_name: str, *items: ParamItem, no_desc: bool = False):
        self.command_name = command_name
        self.description_name = description_name
        self.items: tuple[ParamItem] = items
        self.no = no_desc


def help_generator(child: str, *params: Param) -> str:
    param_help = ""

    for param in params:
        if param.no:
            continue
        param_help += "\n\n"
        param_help += f"{param.description_name}:\n"
        param_help += "\n".join(["  "+f"{item.name} - {item.desc}" for item in param.items])

    return _base + f" {child} {' '.join([f'<{pk.command_name}>' for pk in params])}" + param_help
