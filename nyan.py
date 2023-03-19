import os
import pathlib
import re
import sys
from helper import Param, ParamItem
from helper import Helper

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


def return_(v, e=1):
    print(v)
    exit(e)


# @dataclass
# class VisualConfig:
#     max_cols: int
#     width: int
#     height: int


class Communicator:
    def __init__(self, nyan_a, nyan_b):
        self.nyan_a = nyan_a
        self.nyan_b = nyan_b
        self.a_to_b_fill = False
        self.b_to_a_fill = False
        self.a_to_b = None
        self.b_to_a = None

    def send(self, nyan, data):
        if nyan == self.nyan_a:
            if self.a_to_b_fill:
                raise ValueError("Port is filled!")
            self.a_to_b = data
            self.a_to_b_fill = True
        elif nyan == self.nyan_b:
            if self.b_to_a_fill:
                raise ValueError("Port is filled!")
            self.b_to_a = data
            self.b_to_a_fill = True
        else:
            raise ValueError("Invalid nyan")

    def receive(self, nyan):
        if nyan == self.nyan_a:
            if self.b_to_a_fill is False:
                return None
            self.b_to_a_fill = False
            return self.b_to_a
        elif nyan == self.nyan_b:
            if self.a_to_b_fill is False:
                return None
            self.a_to_b_fill = False
            return self.a_to_b
        else:
            raise ValueError("Invalid nyan")

    def wake_up(self, nyan):
        if nyan == self.nyan_a:
            self.nyan_b.run()
        if nyan == self.nyan_b:
            self.nyan_a.run()


class Nyan:
    def __init__(self, filename, subprocess=False, base=None, debug=False):
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File \"{filename}\" not found")
        self.initialized = False

        if base:
            self.base = base
        else:
            self.base = os.path.dirname(filename)+"/"

        self.program = None
        self.debug = debug

        self.cursor = 0
        self.memory = {}
        self.pointer = 0
        self.module_pointer = 0
        self.mouses = {}

        self.jump_points = {}
        self.next_points = {}

        self.EOF = False

        self.sub = subprocess

    def init(self):
        self.parse_program()
        self.parse_loop_points()
        self.find_mouse_info()
        self.initialized = True
        return self

    def parse_program(self):
        if self.filename.split(".")[-1] != "nyan":
            raise ValueError(f"Invalid file extension .{self.filename.split('.')[-1]} - File extension must be .nyan")
        with open(self.filename, "r") as _f:
            self.program = re.sub(r'"(.?(\\")?)*?"', "", _f.read().replace("\n", "").replace(" ", "")) + " "
        if not self.sub:
            os.chdir(os.path.dirname(self.filename))

    def parse_loop_points(self):
        def _find_match(start_pair):
            next_to = -1
            for j in range(start_pair + 1, len(self.program)):
                if j <= next_to:
                    continue
                if self.program[j] == "-":
                    self.jump_points[j] = start_pair
                    self.next_points[start_pair] = j
                    return j
                if self.program[j] == "~":
                    next_to = _find_match(j)
            raise SyntaxError("No matching - for ~")

        for i in range(len(self.program)):
            if self.program[i] == "~":
                _find_match(i)

    def find_mouse_info(self):
        _mname = ".".join(self.filename.replace(self.base, "").split(".")[:-1] + ["mouse"])
        if not os.path.exists(_mname):
            return
        with open(_mname, "r") as _f:
            for index, line in enumerate(_f.readlines()):
                mobj = re.match(r"(?P<position>\d+):\s*(?P<filename>.*)\n?", line)
                if mobj:
                    try:
                        _pos = int(mobj.group("position"))
                    except ValueError:
                        raise ValueError(f"Invalid mouse position in line {index} - {mobj.group('position')}")
                    if self.sub and _pos == 0:
                        raise ValueError(f"Mouse position 0 is not allowed in module file")
                    _new = Nyan(mobj.group("filename"), subprocess=True, base=self.base, debug=self.debug).init()
                    self.mouses[_pos] = Communicator(self, _new)
                    _new.set_origin(self.mouses[_pos])
                else:
                    raise SyntaxError(f"Invalid mouse info: line {index}")

    def set_origin(self, origin):
        self.mouses[0] = origin

    def run(self):
        while True:
            char = self.program[self.cursor]
            if char == " ":
                if not self.sub:
                    print("\n")
                break
            if char not in "?!냥냐먕먀.,~-뀨:;":
                raise ValueError(f"Invalid character {char} in file {self.filename}")
            match char:
                case "?":
                    self.pointer += 1
                case "!":
                    self.pointer -= 1
                case "냥":
                    self.memory[self.pointer] = self.memory.get(self.pointer, 0) + 1
                case "냐":
                    self.memory[self.pointer] = self.memory.get(self.pointer, 0) - 1
                case "먕":
                    self.module_pointer += 1
                case "먀":
                    self.module_pointer -= 1
                case ";":
                    if self.module_pointer in self.mouses:
                        self.mouses[self.module_pointer].send(self, self.memory.get(self.pointer, 0))
                        self.mouses[self.module_pointer].wake_up(self)
                case ":":
                    if self.module_pointer in self.mouses:
                        _received = self.mouses[self.module_pointer].receive(self)
                        if not _received:
                            return
                        self.memory[self.pointer] = _received
                case ".":
                    if self.debug:
                        print("{" + str(self.memory.get(self.pointer, 0)) + "}", end="")
                    else:
                        print(chr(self.memory.get(self.pointer, 0)), end="")
                case ",":
                    self.memory[self.pointer] = ord(i) if (i := sys.stdin.read(1)) else 0
                case "~":
                    if self.memory.get(self.pointer, 0) == 0:
                        self.cursor = self.next_points[self.cursor]
                case "-":
                    if self.memory.get(self.pointer, 0) != 0:
                        self.cursor = self.jump_points[self.cursor]
                case "뀨":
                    print("{" + str(self.memory.get(self.pointer, 0)) + "}", end="")

            self.cursor += 1
        self.EOF = True


def translate(lang, src, dest):
    print(f"Translating '{src}' to '{dest}'...")
    match lang:
        case "bf":
            mapper = {"<": "!", ">": "?", "+": "냥", "-": "냐", "[": "~", "]": "-", ",": ",", ".": ".", ' ': ' ',
                      '\n': "\n"}
            with open(src, "r") as _f:
                origin_program = _f.read()
            source = ""
            comment_mode = False
            for char in origin_program:
                if char not in "<>+-[],. \n":
                    if not comment_mode:
                        source += "\""
                    comment_mode = True
                    source += char
                else:
                    if char == " " and comment_mode:
                        source += char
                        continue
                    if comment_mode:
                        comment_mode = False
                        source += "\""
                    source += mapper[char]
            if comment_mode:
                source += "\""
            with open(dest, "w") as _f:
                _f.write(source)


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
    case [_, "translate", language]:
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
