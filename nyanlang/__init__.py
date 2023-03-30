from .nyan import Nyan, NyanEngine

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
        )
    ),
    "run": helpgen.help(
        "run",
        Param("filename", "", no_desc=True),
        Param("debug", "", no_desc=True, optional=True, kw="d")
    )
}


def main():
    match sys.argv:
        case [_]:
            return_(HELP["_"])
        case [_, "run"]:
            return_(HELP["run"])
        case [_, "run", f, *options]:
            debug = False
            if "-d" in options or "--debug" in options:
                debug = True
            NyanEngine(f, debug=debug).run()
        case cmd:
            try:
                __import__("nyan_ext_"+cmd[1]).run()
            except ModuleNotFoundError:
                return_(f"Invalid command \"{sys.argv[1]}\"")


if __name__ == "__main__":
    main()
