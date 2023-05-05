from .nyan import NyanInterpreter, NyanEngine, NyanBuilder

from .helper import Param, ParamItem
from .helper import Helper

import sys


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
    ),
    "build": helpgen.help(
        "build",
        Param("filename", "", no_desc=True),
        Param("out", "", no_desc=True, optional=True, kw="o")
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
        case [_, "build"]:
            return_(HELP["build"])
        case [_, "build", f, *options]:
            out = None
            if "-o" in options:
                if len(options) == options.index("-o")+1:
                    raise IndexError("'-o' parameter value not specified.")
                out = options[options.index("-o")+1]
            elif "--out" in options:
                if len(options) == options.index("--out")+1:
                    raise IndexError("'--out' parameter value not specified.")
            NyanBuilder(f).build(output=out)
        case cmd:
            try:
                __import__("nyan_ext_"+cmd[1]).run()
            except ModuleNotFoundError:
                return_(f"Invalid command \"{sys.argv[1]}\"")


if __name__ == "__main__":
    main()
