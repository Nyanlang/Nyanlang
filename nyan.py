import sys
import os
import pathlib
import re
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
            ParamItem("translate", "Translate a file to nyanlang language from other language")
        )
    ),
    "run": helpgen.help(
        "run",
        Param("filename", "", no_desc=True)
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
    )
}

LANG = {
    "bf": ["b", "bf"]
}


def return_(v, e=1):
    print(v)
    exit(e)


def run(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")

    with open(filename, "r") as f:
        program = re.sub(r'".*?"', "", f.read().replace("\n", "").replace(" ", "") + " ")

    jump_points = {}
    next_points = {}

    def find_matchpoint(start_pair):
        next_to = -1
        for i in range(start_pair+1, len(program)):
            if i <= next_to:
                continue
            if program[i] == "-":
                jump_points[i] = start_pair
                next_points[start_pair] = i
                return i
            if program[i] == "~":
                next_to = find_matchpoint(i)
        raise SyntaxError("No matching - for ~")

    for i in range(len(program)):
        if program[i] == "~":
            find_matchpoint(i)

    pointer = 0
    memory = {}
    cursor = 0

    while cursor < len(program):
        char = program[cursor]
        if char == " ":
            break
        if char not in "?!냥냐.,~-뀨":
            raise ValueError(f"Invalid character {char}")
        match char:
            case "?":
                pointer += 1
            case "!":
                pointer -= 1
            case "냥":
                memory[pointer] = memory.get(pointer, 0) + 1
            case "냐":
                memory[pointer] = memory.get(pointer, 0) - 1
            case ".":
                print(chr(memory.get(pointer, 0)), end="")
            case ",":
                memory[pointer] = ord((lambda ip: ip[0] if len(ip) >= 1 else 0)(input()))
            case "~":
                if memory.get(pointer, 0) == 0:
                    cursor = next_points[cursor]
            case "-":
                if memory.get(pointer, 0) != 0:
                    cursor = jump_points[cursor]
            case "뀨":
                print(memory.get(pointer, 0))

        cursor += 1


def translate(lang, src, dest):
    print(f"Translating '{src}' to '{dest}'...")
    match lang:
        case "bf":
            mapper = {"<": "!", ">": "?", "+": "냥", "-": "냐", "[": "~", "]": "-", ",": ",", ".": ".", ' ': ' ',
                      '\n': "\n"}
            with open(src, "r") as f:
                origin_program = f.read()
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
            with open(dest, "w") as f:
                f.write(source)


match sys.argv:
    case [_]:
        return_(HELP["_"])
    case [_, "run"]:
        return_(HELP["run"])
    case [_, "run", *f]:
        if ' '.join(f).split(".")[-1] != "nyan":
            raise ValueError(f"Invalid file extension .{' '.join(f).split('.')[-1]} - File extension must be .nyan")
        run(' '.join(f))
    case [_, "translate"]:
        return_(HELP["translate"])
    case [_, "translate", language]:
        return_(HELP["translate"])
    case [_, "translate", language, *f]:
        _dest = None
        if "--dest" in f:
            _dest = pathlib.Path(' '.join(f[f.index("--dest")+1:]))
            f = f[:f.index("--dest")]

        if language not in LANG:
            raise ValueError(f"Invalid language {language}")

        if ' '.join(f).split(".")[-1] not in LANG[language]:
            raise ValueError(f"Invalid file extension .{' '.join(f).split('.')[-1]} - "
                             f"File extension must be {'or'.join(['.'+i for i in LANG[language]])}")

        if not pathlib.Path(" ".join(f)).exists():
            raise FileNotFoundError(f"File {' '.join(f)} not found")

        if not _dest:
            _dest = pathlib.Path('.'.join(" ".join(f).split(".")[:-1] + ["nyan"]))

        if _dest.exists():
            raise FileExistsError(f"File {_dest} already exists")

        translate(language, " ".join(f), _dest)
    case _:
        raise ValueError(f"Invalid command {sys.argv}")
