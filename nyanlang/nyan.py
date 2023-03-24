import os
from pathlib import Path
import re
import sys
import logging

logging.basicConfig(level=logging.ERROR)


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
            self.a_to_b = data
            self.a_to_b_fill = True
        elif nyan == self.nyan_b:
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

    def get_nyan(self, nyan):
        if nyan == self.nyan_a:
            return self.nyan_b
        elif nyan == self.nyan_b:
            return self.nyan_a
        else:
            raise ValueError("Invalid nyan")


class CommunitySignal:
    SEND_WAKE = 0
    RECEIVE_WAKE = 1
    MAIN_EOF = 2
    SUB_EOF = 3


class Nyan:
    def __init__(self, filename: Path, subprocess=False, debug=False):
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File \"{filename}\" not found")
        self.initialized = False

        self.program = None
        self.debug = debug

        self.cursor = 0
        self.memory = {}
        self.pointer = 0
        self.module_pointer = 0
        self.pointing_parents = False
        self.children = {}
        self.parents = {}

        self.jump_points = {}
        self.next_points = {}

        self.sub = subprocess

    def init(self):
        self.parse_program()
        self.parse_loop_points()
        self.initialized = True
        return self

    def reset(self):
        self.cursor = 0
        self.memory = {}
        self.pointer = 0
        self.module_pointer = 0

    def add_parent(self, parent: Communicator, pos: int):
        if pos in self.parents:
            raise ValueError("Parent cat already exists")
        self.parents[pos] = parent

    def add_child(self, child: Communicator, pos: int):
        if pos in self.children:
            raise ValueError("Child cat already exists")
        self.children[pos] = child

    def parse_program(self):
        if self.filename.suffix != ".nyan":
            raise ValueError(f"Invalid file extension {self.filename.suffix} - File extension must be .nyan")
        with open(self.filename, "r") as _f:
            self.program = re.sub(r'"(.?(\\")?)*?"', "", _f.read().replace("\n", "").replace(" ", "")) + " "

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

    def run(self):
        while True:
            char = self.program[self.cursor]
            if char == " ":
                if not self.sub:
                    print("\n")
                break
            if char not in "?!냥냐먕먀.,~-뀨:;'":
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
                    if self.pointing_parents:
                        if self.module_pointer in self.parents:
                            self.parents[self.module_pointer].send(self, self.memory.get(self.pointer, 0))
                            self.cursor += 1
                            return CommunitySignal.SEND_WAKE, self.module_pointer
                        else:
                            raise ValueError("Parent cat does not exist")
                    else:
                        if self.module_pointer in self.children:
                            self.children[self.module_pointer].send(self, self.memory.get(self.pointer, 0))
                            self.cursor += 1
                            return CommunitySignal.SEND_WAKE, self.module_pointer
                        else:
                            raise ValueError("Child cat does not exist")
                case ":":
                    if self.pointing_parents:
                        if self.module_pointer in self.parents:
                            _received = self.parents[self.module_pointer].receive(self)
                            if not _received:
                                self.cursor += 1
                                return CommunitySignal.RECEIVE_WAKE, self.module_pointer
                            self.memory[self.pointer] = _received
                        else:
                            raise ValueError("Parent cat does not exist")
                    else:
                        if self.module_pointer in self.children:
                            _received = self.children[self.module_pointer].receive(self)
                            if not _received:
                                self.cursor += 1
                                return CommunitySignal.RECEIVE_WAKE, self.module_pointer
                            self.memory[self.pointer] = _received
                        else:
                            raise ValueError("Child cat does not exist")
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
                case "'":
                    self.pointing_parents = not self.pointing_parents

            self.cursor += 1
        if self.sub:
            return CommunitySignal.SUB_EOF, self.module_pointer
        return CommunitySignal.MAIN_EOF, self.module_pointer


class NyanEngine:
    def __init__(self, root_name: str, *, debug=False):
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

        self.root = Nyan(Path(root_name).absolute(), debug=self.debug).init()
        self.references = {}

        self.find_mouse_info()

    def find_mouse_info(self, nyan: Nyan | None = None):
        if not nyan:
            _mpath = os.path.join(self.root.filename.parent, self.root.filename.stem + ".mouse")
        else:
            _mpath = os.path.join(nyan.filename.parent, nyan.filename.stem + ".mouse")
        if not os.path.exists(_mpath):
            return
        with open(_mpath, "r") as _f:
            for index, line in enumerate(_f.readlines()):
                mobj = re.match(r"(?P<position>-?\d+)->(?P<target_pos>-?\d+):\s*(?P<filename>.*)\n?", line)
                if mobj:
                    try:
                        _pos = int(mobj.group("position"))
                        _tpos = int(mobj.group("target_pos"))
                    except ValueError:
                        raise ValueError(f"Invalid mouse position in line {index} - "
                                         f"{mobj.group('position')} or {mobj.group('target_pos')}")
                    new_path = Path(
                        os.path.join(
                            (self.root.filename.parent if not nyan else nyan.filename.parent),
                            Path(mobj.group("filename"))
                        )
                    ).absolute()
                    if new_path not in self.references:
                        _child = Nyan(new_path, subprocess=True, debug=self.debug).init()
                        self.references[new_path] = _child
                    else:
                        _child = self.references[new_path]
                    if not nyan:
                        _comm = Communicator(self.root, _child)
                        self.root.add_child(_comm, _pos)
                    else:
                        _comm = Communicator(nyan, _child)
                        nyan.add_child(_comm, _pos)
                    _child.add_parent(_comm, _tpos)
                    self.find_mouse_info(_child)
                else:
                    raise SyntaxError(f"Invalid mouse info: line {index}")

    def run(self, nyan: Nyan = None):
        if not nyan:
            nyan = self.root
        while True:
            signal, mouse_pointer = nyan.run()
            match signal:
                case CommunitySignal.SEND_WAKE:
                    if nyan.sub and mouse_pointer == 0:
                        return
                    self.run(nyan.children[mouse_pointer].get_nyan(nyan))
                case CommunitySignal.RECEIVE_WAKE:
                    if nyan.sub and mouse_pointer == 0:
                        return
                    self.run(nyan.children[mouse_pointer].get_nyan(nyan))
                case CommunitySignal.SUB_EOF:
                    nyan.reset()
                    return
                case CommunitySignal.MAIN_EOF:
                    return


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
