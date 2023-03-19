from .nyan import Nyan, translate

from .helper import Param, ParamItem
from .helper import Helper

import sys
import pathlib


def return_(v, e=1):
    print(v)
    exit(e)


helpgen = Helper(__file__)

HELP = {
    "_": helpgen.help(
        "",
        Param(
            "command",
            "Commands",
            ParamItem("run", "Run a file"),
            ParamItem("translate", "Translate a file to nyanlang language from other language"),
            ParamItem("visual", "Visualize nyanlang memory")
        )
    ),
    "run": helpgen.help(
        "run",
        Param("filename", "", no_desc=True),
        Param("debug", "", no_desc=True, optional=True, kw="d")
    ),
    "translate": helpgen.help(
        "translate",
        Param(
            "language",
            "Languages",
            ParamItem("bf", "Brainfuck"),
        ),
        Param("filename", "", no_desc=True),
        Param("destination", "", no_desc=True, optional=True, kw="dest")
    ),
    # "visual": helpgen.help(
    #     "visual",
    #     Param("filename", "", no_desc=True),
    #     Param("max_cols", "", no_desc=True, optional=True, kw="cols"),
    #     Param("width", "", no_desc=True, optional=True, kw="w"),
    #     Param("height", "", no_desc=True, optional=True, kw="h"),
    # )
}

LANG = {
    "bf": ["b", "bf"]
}


def run():
    match sys.argv:
        case [_]:
            return_(HELP["_"])
        case [_, "run"]:
            return_(HELP["run"])
        case [_, "run", f, *options]:
            debug = False
            if "--d" in options:
                debug = True
            Nyan(f, debug=debug).init().run()
        case [_, "translate"]:
            return_(HELP["translate"])
        case [_, "translate", _]:
            return_(HELP["translate"])
        case [_, "translate", language, f, *options]:
            _dest = None
            if "--dest" in options:
                _dest = pathlib.Path(options[options.index("--dest")+1])

            if language not in LANG:
                raise ValueError(f"Invalid language {language}")

            if f.split(".")[-1] not in LANG[language]:
                raise ValueError(f"Invalid file extension .{' '.join(f).split('.')[-1]} - "
                                 f"File extension must be {'or'.join(['.'+i for i in LANG[language]])}")

            if not pathlib.Path(f).exists():
                raise FileNotFoundError(f"File {f} not found")

            if not _dest:
                _dest = pathlib.Path('.'.join(f.split(".")[:-1] + ["nyan"]))

            if _dest.exists():
                raise FileExistsError(f"File {_dest} already exists")

            translate(language, f, _dest)
        # case [_, "visual"]:
        #     return_(HELP["visual"])
        # case [_, "visual", f, *options]:
        #     _cols = None
        #     if "--cols" in options:
        #         _cols = int(options[options.index("--cols")+1])

        #     _w = None
        #     if "--w" in options:
        #         _w = int(options[options.index("--w")+1])

        #     _h = None
        #     if "--h" in options:
        #         _h = int(options[options.index("--h")+1])

        #     if f.split(".")[-1] != "nyan":
        #         raise ValueError(f"Invalid file extension .{f.split('.')[-1]} - File extension must be .nyan")
        case _:
            raise ValueError(f"Invalid command {sys.argv}")


if __name__ == "__main__":
    run()
