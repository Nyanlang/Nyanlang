class ParamItem:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc


class Param:
    def __init__(
            self, command_name: str, description_name: str,
            *items: ParamItem,
            no_desc: bool = False,
            optional: bool = False,
            kw: str = None
    ):
        self.command_name = f"[{command_name}?]" if optional else f"<{command_name}>"
        self.description_name = description_name
        self.items: tuple[ParamItem] = items
        self.no = no_desc
        if kw:
            self.command_name = self.command_name[:1] + f"--{kw} " + self.command_name[1:]


class Helper:
    def __init__(self, file):
        self.file = file
        self._base = f"Usage: nyan"

    def help(self, child: str, *params: Param) -> str:
        param_help = ""

        for param in params:
            if param.no:
                continue
            param_help += "\n\n"
            param_help += f"{param.description_name}:\n"
            param_help += "\n".join(["  "+f"{item.name} - {item.desc}" for item in param.items])

        return self._base + f" {child} {' '.join([f'{pk.command_name}' for pk in params])}" + param_help
