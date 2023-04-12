import os
from pathlib import Path
import re
import sys
import logging

logging.basicConfig(level=logging.ERROR)

_logger = logging.getLogger("NyanEngine")


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


class Signals:
    PAUSE = 0
    MAIN_EOF = 2
    SUB_EOF = 3
    KEEP_GOING = 4


class Pointer:
    def __init__(self, initial: int = None):
        if initial is None:
            initial = 0
        self._v = initial

    def increase(self):
        self._v += 1

    def decrease(self):
        self._v -= 1

    def set(self, value: int):
        self._v = value

    def __int__(self):
        return self._v


class Memory:
    def __init__(self, initial: dict = None):
        if initial is None:
            initial = {}
        self.memory = initial

    def increase(self, pointer: Pointer):
        self.memory[int(pointer)] = self.memory.get(int(pointer), 0) + 1

    def decrease(self, pointer: Pointer):
        self.memory[int(pointer)] = self.memory.get(int(pointer), 0) - 1

    def set(self, pointer: Pointer, value: int):
        self.memory[int(pointer)] = value

    def get(self, pointer: Pointer):
        return self.memory.get(int(pointer), 0)


class NyanInterpreter:
    def __init__(self, filename: Path, subprocess=False, debug=False):
        self.filename = filename
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File \"{filename}\" not found")
        self.initialized = False

        self.program = None
        self.debug = debug

        self.cursor = 0
        self.memory = Memory()
        self.pointer = Pointer()
        self.module_pointer = Pointer()
        self.pointing_parents = False
        self.children = {}
        self.parents = {}

        self.jump_points = {}
        self.next_points = {}

        self.keywords = {
            "?": lambda o: o.pointer.increase(),
            "!": lambda o: o.pointer.decrease(),
            "냥": lambda o: o.memory.increase(o.pointer),
            "냐": lambda o: o.memory.decrease(o.pointer),
            "먕": lambda o: o.module_pointer.increase(),
            "먀": lambda o: o.module_pointer.decrease(),
            ";": ...,
            ":": ...,
            ".": lambda o: print(chr(o.memory.get(o.pointer)), end=""),
            ",": lambda o: o.memory.set(o.pointer, ord(i) if (i := sys.stdin.read(1)) else 0),
            "뀨": lambda o: print("{"+str(o.memory.get(o.pointer))+"}", end=""),
        }
        self.module_write()
        self.module_read()
        self.module_control()
        self.jumper_end()
        self.jumper_start()

        self.sub = subprocess

    def init(self):
        self.parse_program()
        self.parse_loop_points()
        self.initialized = True
        _logger.debug(f"Nyan \"{self.filename.stem}\" initialized.")
        return self

    def reset(self):
        self.cursor = 0
        self.memory = {}
        self.pointer = 0
        self.module_pointer = 0
        self.pointing_parents = False
        _logger.debug(f"Nyan \"{self.filename.stem}\" initialized.")

    def add_keyword(self, keyword: str):
        def wrapper(handler: callable):
            self.keywords[keyword] = handler
        return wrapper

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
        with open(self.filename, "r", encoding="utf-8") as _f:
            self.program = re.sub(r'"(.?(\\")?)*?"', "", _f.read().replace("\n", "").replace(" ", "")) + "    "

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

    def before_run(self):
        ...

    def after_run(self):
        ...

    def start_of_loop(self):
        ...

    def end_of_loop(self):
        ...

    def module_read(self):
        def wrapper(o):
            if o.pointing_parents:
                if o.module_pointer in o.parents:
                    _received = o.parents[o.module_pointer].receive(o)
                    if not _received:
                        return Signals.PAUSE, o.pointing_parents, o.module_pointer
                    o.memory[o.pointer] = _received
                else:
                    raise ValueError("Parent cat does not exist")
            else:
                if o.module_pointer in o.children:
                    _received = o.children[o.module_pointer].receive(o)
                    if not _received:
                        return Signals.PAUSE, o.pointing_parents, o.module_pointer
                    o.memory[o.pointer] = _received
                else:
                    raise ValueError("Child cat does not exist")
        self.add_keyword(":")(wrapper)

    def module_write(self):
        def wrapper(o):
            if o.pointing_parents:
                if o.module_pointer in o.parents:
                    o.parents[o.module_pointer].send(o, o.memory.get(o.pointer, 0))
                    o.cursor += 1
                    return Signals.PAUSE, o.pointing_parents, o.module_pointer
                else:
                    raise ValueError("Parent cat does not exist")
            else:
                if o.module_pointer in o.children:
                    o.children[o.module_pointer].send(o, o.memory.get(o.pointer, 0))
                    o.cursor += 1
                    return Signals.PAUSE, o.pointing_parents, o.module_pointer
                else:
                    raise ValueError("Child cat does not exist")
        self.add_keyword(";")(wrapper)

    def jumper_start(self):
        def wrapper(o):
            if o.memory.get(o.pointer) == 0:
                o.cursor = o.next_points[o.cursor]
        self.add_keyword("~")(wrapper)

    def jumper_end(self):
        def wrapper(o):
            if o.memory.get(o.pointer, 0) != 0:
                o.cursor = o.jump_points[o.cursor]
        self.add_keyword("-")(wrapper)

    def module_control(self):
        def wrapper(o):
            o.pointing_parents = not o.pointing_parents
        self.add_keyword("'")(wrapper)

    def run(self):
        self.before_run()
        while True:
            self.start_of_loop()
            char = self.program[self.cursor]
            if char == " ":
                if not self.sub:
                    print("\n")
                break
            if char in self.keywords:
                raw_response = self.keywords[char](self)
                if type(raw_response) == tuple:
                    return raw_response
            else:
                raise SyntaxError(f"Invalid character {char}")

            self.cursor += 1
            self.end_of_loop()
        if self.sub:
            return Signals.SUB_EOF, self.pointing_parents, self.module_pointer
        return Signals.MAIN_EOF, self.pointing_parents, self.module_pointer


class NyanEngine:
    def __init__(self, root_name: str, *, debug=False):
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            _logger.level = logging.DEBUG

        self.root = NyanInterpreter(Path(root_name).absolute(), debug=self.debug).init()
        self.nodetree = []
        self.references = {}

        self.nyans = [self.root]

        self.find_mouse_info()

    def find_mouse_info(self, nyan: NyanInterpreter | None = None):
        if not nyan:
            _mpath = os.path.join(self.root.filename.parent, self.root.filename.stem + ".mouse")
        else:
            _mpath = os.path.join(nyan.filename.parent, nyan.filename.stem + ".mouse")
        if not os.path.exists(_mpath):
            return
        with open(_mpath, "r", encoding="utf-8") as _f:
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
                        _child = NyanInterpreter(new_path, subprocess=True, debug=self.debug).init()
                        self.references[new_path] = _child
                        self.nyans.append(_child)
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

    def run(self):
        while True:
            if not self.nodetree:
                nyan = self.root
            else:
                nyan = self.nodetree[-1]
            _logger.debug(f"Running {nyan.filename.stem}")
            signal, parent_mode, mouse_pointer = nyan.run()
            match signal:
                case Signals.PAUSE:
                    if parent_mode:
                        points = nyan.parents[mouse_pointer].get_nyan(nyan)
                    else:
                        points = nyan.children[mouse_pointer].get_nyan(nyan)
                    if len(self.nodetree) >= 2 and self.nodetree[-2] == points:
                        self.nodetree = self.nodetree[:-1]
                        continue
                    self.nodetree.append(points)
                    continue
                case Signals.SUB_EOF:
                    nyan.reset()
                    self.nodetree = self.nodetree[:-1]
                    continue
                case Signals.MAIN_EOF:
                    return
