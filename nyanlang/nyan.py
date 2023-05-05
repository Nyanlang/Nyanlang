import os
from pathlib import Path
import re
import sys
import logging

logging.basicConfig(level=logging.ERROR)

_logger = logging.getLogger("NyanEngine")


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
    def __init__(self, initial=None):
        if initial is None:
            initial = 0
        self._v = initial

    def increase(self):
        self._v += 1

    def decrease(self):
        self._v -= 1

    def set(self, value):
        self._v = value

    def get(self):
        return self._v


class Memory:
    def __init__(self, initial=None):
        if initial is None:
            initial = {}
        self.memory = initial

    def increase(self, pointer):
        self.memory[pointer.get()] = self.memory.get(pointer.get(), 0) + 1

    def decrease(self, pointer):
        self.memory[pointer.get()] = self.memory.get(pointer.get(), 0) - 1

    def set(self, pointer, value):
        self.memory[pointer.get()] = value

    def get(self, pointer):
        return self.memory.get(pointer.get(), 0)


class ProgramParser:
    def __init__(self, filename):
        self.filename = filename
        self.program = None

    def parse(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File \"{self.filename}\" not found")
        if self.filename.suffix != ".nyan":
            raise ValueError(f"Invalid file extension {self.filename.suffix} - File extension must be .nyan")
        with open(self.filename, "r", encoding="utf-8") as _f:
            self.program = re.sub(r'"(.?(\\")?)*?"', "", _f.read().replace("\n", "").replace(" ", "")) + "    "
        return self.program


class NyanInterpreter:
    def __init__(self, filename, subprocess=False, debug=False):
        self.filename = filename
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
        self.memory = Memory()
        self.pointer = Pointer()
        self.module_pointer = Pointer()
        self.pointing_parents = False
        _logger.debug(f"Nyan \"{self.filename.stem}\" initialized.")

    def add_keyword(self, keyword):
        def wrapper(handler):
            self.keywords[keyword] = handler
        return wrapper

    def add_parent(self, parent, pos):
        if pos in self.parents:
            raise ValueError("Parent cat already exists")
        self.parents[pos] = parent

    def add_child(self, child, pos):
        if pos in self.children:
            raise ValueError("Child cat already exists")
        self.children[pos] = child

    def parse_program(self):
        self.program = ProgramParser(self.filename).parse()

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

    def module_read(self, keyword=":"):
        def wrapper(o):
            if o.pointing_parents:
                if o.module_pointer.get() in o.parents:
                    _received = o.parents[o.module_pointer.get()].receive(o)
                    if not _received:
                        return Signals.PAUSE, o.pointing_parents, o.module_pointer.get()
                    o.memory.set(o.pointer, _received)
                else:
                    raise ValueError("Parent cat does not exist")
            else:
                if o.module_pointer.get() in o.children:
                    _received = o.children[o.module_pointer.get()].receive(o)
                    if not _received:
                        return Signals.PAUSE, o.pointing_parents, o.module_pointer.get()
                    o.memory.set(o.pointer, _received)
                else:
                    raise ValueError("Child cat does not exist")
        self.add_keyword(keyword)(wrapper)

    def module_write(self, keyword=";"):
        def wrapper(o):
            if o.pointing_parents:
                if o.module_pointer.get() in o.parents:
                    o.parents[o.module_pointer.get()].send(o, o.memory.get(o.pointer))
                    o.cursor += 1
                    return Signals.PAUSE, o.pointing_parents, o.module_pointer.get()
                else:
                    raise ValueError("Parent cat does not exist")
            else:
                if o.module_pointer.get() in o.children:
                    o.children[o.module_pointer.get()].send(o, o.memory.get(o.pointer))
                    o.cursor += 1
                    return Signals.PAUSE, o.pointing_parents, o.module_pointer.get()
                else:
                    raise ValueError("Child cat does not exist")
        self.add_keyword(keyword)(wrapper)

    def jumper_start(self, keyword="~"):
        def wrapper(o):
            if o.memory.get(o.pointer) == 0:
                o.cursor = o.next_points[o.cursor]
        self.add_keyword(keyword)(wrapper)

    def jumper_end(self, keyword="-"):
        def wrapper(o):
            if o.memory.get(o.pointer) != 0:
                o.cursor = o.jump_points[o.cursor]
        self.add_keyword(keyword)(wrapper)

    def module_control(self, keyword="'"):
        def wrapper(o):
            o.pointing_parents = not o.pointing_parents
        self.add_keyword(keyword)(wrapper)

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


class NyanBinaryInterpreter(NyanInterpreter):
    def __init__(self, filename, subprocess=False, debug=False):
        super().__init__(filename, subprocess, debug)
        sample = NyanInterpreter(Path("."))
        _temp = {}
        for k, v in NyanBuilder.keywords.items():
            _temp[v] = sample.keywords[k]
        self.keywords = {**_temp}
        self.constant_program = None

    def add_binary_keyword(self, keyword):
        def wrapper(handler):
            self.keywords[keyword] = handler
        return wrapper

    def parse_program(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File \"{self.filename}\" not found")
        if self.filename.suffix != ".nya":
            raise ValueError(f"Invalid file extension {self.filename.suffix} - File extension must be .nya")
        with open(self.filename, "rb") as _f:
            self.program = _f.read()
            self.constant_program = self.program
            if self.program[0].to_bytes(1, "big") == b"\x00":
                cursor = 3
                for _ in range(int(self.program[1:3].hex(), 16)):
                    filename_break = self.program.index(b"\x0a", cursor+4) + 1
                    cursor += filename_break - cursor
                self.program = self.program[cursor:]
            elif self.program[0].to_bytes(1, "big") == b"\x01":
                self.program = self.program[1:]
            else:
                raise SyntaxError(f"Invalid start byte {self.program[0].to_bytes(1, 'big')}")

    def parse_loop_points(self):
        def _find_match(start_pair):
            next_to = -1
            find_point = start_pair + 1
            while find_point <= len(self.program):
                char = self.program[find_point].to_bytes(1, "big")
                if find_point > next_to:
                    if char == NyanBuilder.keywords["-"]:
                        self.jump_points[find_point] = start_pair
                        self.next_points[start_pair] = find_point
                        return find_point
                    if char == NyanBuilder.keywords["~"]:
                        next_to = _find_match(find_point)
                if char in NyanBuilder.compress_target:
                    find_point += 4
                else:
                    find_point += 1
            raise SyntaxError("No matching - for ~")

        cursor = 0
        while cursor < len(self.program):
            char = self.program[cursor].to_bytes(1, "big")
            if char == NyanBuilder.keywords["~"]:
                _find_match(cursor)
            if char in NyanBuilder.compress_target:
                cursor += 4
            else:
                cursor += 1

    def run(self):
        self.before_run()
        while True:
            self.start_of_loop()
            try:
                char = self.program[self.cursor].to_bytes(1, 'big')
            except IndexError:
                break
            if char in NyanBuilder.compress_target:
                times = int(self.program[self.cursor + 1:self.cursor + 4].hex(), 16)
                for _ in range(times):
                    self.keywords[char](self)
                self.cursor += 4
            else:
                raw_response = self.keywords[char](self)
                if type(raw_response) == tuple:
                    return raw_response
                self.cursor += 1
            self.end_of_loop()
        if self.sub:
            return Signals.SUB_EOF, self.pointing_parents, self.module_pointer
        return Signals.MAIN_EOF, self.pointing_parents, self.module_pointer


class NyanEngine:
    def __init__(self, root_name, *, debug=False):
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            _logger.level = logging.DEBUG

        path = Path(root_name).absolute()
        if path.suffix == ".nya":
            self.root = NyanBinaryInterpreter(Path(root_name).absolute(), debug=self.debug).init()
        else:
            self.root = NyanInterpreter(Path(root_name).absolute(), debug=self.debug).init()
        self.nodetree = []
        self.references = {}

        self.nyans = [self.root]

        if path.suffix == ".nya":
            self.find_binary_mouse_info()
        else:
            self.find_mouse_info()

    def read_mouse(self, path):
        with open(path, "r", encoding="utf-8") as _f:
            for index, line in enumerate(_f.readlines()):
                mobj = re.match(r"(?P<position>-?\d+)\s*->\s*(?P<target_pos>-?\d+):\s*(?P<filename>.*)\n?", line)
                if not mobj:
                    raise SyntaxError(f"Invalid mouse info: line {index}")
                try:
                    _pos = int(mobj.group("position"))
                    _tpos = int(mobj.group("target_pos"))
                    _file = str(mobj.group("filename"))
                except ValueError:
                    raise ValueError(f"Invalid mouse position in line {index} - "
                                     f"{mobj.group('position')} or {mobj.group('target_pos')}")
                yield _pos, _tpos, _file

    def mouse_exists(self, nyan=None):
        if not nyan:
            _mpath = os.path.join(self.root.filename.parent, self.root.filename.stem + ".mouse")
        else:
            _mpath = os.path.join(nyan.filename.parent, nyan.filename.stem + ".mouse")
        if not os.path.exists(_mpath):
            return ""
        return _mpath

    def find_mouse_info(self, nyan=None):
        if not (_mpath := self.mouse_exists(nyan)):
            return
        with open(_mpath, "r", encoding="utf-8") as _f:
            for pos, tpos, filename in self.read_mouse(_mpath):
                new_path = Path(
                    os.path.join(
                        (self.root.filename.parent if not nyan else nyan.filename.parent),
                        Path(filename)
                    )
                ).absolute()
                child_is_binary = False
                if new_path.suffix == ".nya":
                    child_is_binary = True
                if new_path not in self.references:
                    if child_is_binary:
                        _child = NyanBinaryInterpreter(new_path, subprocess=True, debug=self.debug).init()
                    else:
                        _child = NyanInterpreter(new_path, subprocess=True, debug=self.debug).init()
                    self.references[new_path] = _child
                    self.nyans.append(_child)
                else:
                    _child = self.references[new_path]
                if not nyan:
                    _comm = Communicator(self.root, _child)
                    self.root.add_child(_comm, pos)
                else:
                    _comm = Communicator(nyan, _child)
                    nyan.add_child(_comm, pos)
                _child.add_parent(_comm, tpos)
                if child_is_binary:
                    self.find_binary_mouse_info(_child)
                else:
                    self.find_mouse_info(_child)

    def read_binary_mouse(self, path):
        count = int(path[1:3].hex(), 16)
        cursor = 3
        for _ in range(count):
            pos = int(path[cursor:cursor+2].hex(), 16)
            tpos = int(path[cursor+2:cursor+4].hex(), 16)
            filename_break = path.index(b"\x0a", cursor+4)+1
            filename = path[cursor+4:filename_break].decode(encoding="utf-8")[2:-1]
            yield pos, tpos, filename
            cursor += filename_break - cursor

    def binary_mouse_exists(self, data):
        if data[0].to_bytes(1, 'big') == b"\x00":
            return True
        else:
            return False

    def find_binary_mouse_info(self, nyan=None):
        if nyan:
            target_nyan = nyan
        else:
            target_nyan = self.root
        if not self.binary_mouse_exists(target_nyan.constant_program):
            return
        for pos, tpos, filename in self.read_binary_mouse(target_nyan.constant_program):
            new_path = Path(
                os.path.join(
                    (self.root.filename.parent if not nyan else nyan.filename.parent),
                    Path(filename)
                )
            ).absolute()
            child_is_binary = False
            if new_path.suffix == ".nya":
                child_is_binary = True
            if new_path not in self.references:
                if child_is_binary:
                    _child = NyanBinaryInterpreter(new_path, subprocess=True, debug=self.debug).init()
                else:
                    _child = NyanInterpreter(new_path, subprocess=True, debug=self.debug).init()
                self.references[new_path] = _child
                self.nyans.append(_child)
            else:
                _child = self.references[new_path]
            _comm = Communicator(target_nyan, _child)
            target_nyan.add_child(_comm, pos)
            _child.add_parent(_comm, tpos)
            if child_is_binary:
                self.find_binary_mouse_info(_child)
            else:
                self.find_mouse_info(_child)

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


class NyanBuilder(NyanEngine):
    keywords = {
        "?": b"\x00",
        "!": b"\x01",
        "냥": b"\x02",
        "냐": b"\x03",
        "먕": b"\x04",
        "먀": b"\x05",
        ";": b"\x06",
        ":": b"\x07",
        ".": b"\x08",
        ",": b"\x09",
        "'": b"\x0a",
        "~": b"\x0b",
        "-": b"\x0c",
        "뀨": b"\x0d",
    }

    compress_target = b"\x00\x01\x02\x03\x04\x05\x08\x09"

    def __init__(self, root_name, *, debug=False):
        self.program = []
        super().__init__(root_name, debug=debug)

    @staticmethod
    def byte_add(byte, count=1):
        return (int(byte.hex(), 16)+count).to_bytes(3, 'big')

    def find_mouse_info(self, nyan=None):
        _mpath = os.path.join(self.root.filename.parent, self.root.filename.stem + ".mouse")
        if not os.path.exists(_mpath):
            self.program.append(b"\x01")
        else:
            self.program.append(b"\x00")
            mouse_count = 0
            for pos, tpos, filename in self.read_mouse(_mpath):
                mouse_count += 1
                print(
                    pos, tpos, filename
                )
                print(
                    pos.to_bytes(2, 'big') + bytes(1)
                    + pos.to_bytes(2, 'big') + bytes(1)
                    + filename.encode(encoding="utf-8") + b"\x0a"
                )
                self.program.append(
                    pos.to_bytes(2, 'big')+bytes(1)
                    + pos.to_bytes(2, 'big')+bytes(1)
                    + filename.encode(encoding="utf-8")+b"\x0a"
                )
            self.program.insert(1, mouse_count.to_bytes(2, 'big'))

    def build(self, output=None):
        if output:
            out = Path(output).absolute()
            if not out.exists():
                raise ValueError("Output path not found.")
            if out.suffix != ".nya":
                raise ValueError("Output file suffix must end with .nya")
        else:
            out = Path(self.root.filename.stem+".nya")
        if not self.nodetree:
            nyan = self.root
        else:
            nyan = self.nodetree[-1]
        _logger.info(f"Building {nyan.filename.stem}")
        # code validation
        if nyan.program.count("~") != nyan.program.count("-"):
            raise SyntaxError("LoopPointNotMatching")

        for char in nyan.program:
            if char == " ":
                break
            if char not in self.keywords:
                raise SyntaxError(f"Invalid character {char}")
            bytechar = self.keywords[char]
            if bytechar in self.compress_target:
                if len(self.program) == 0 or self.program[-1][0:1] != bytechar:
                    self.program.append(bytechar+b"\x00\x00\x01")
                    continue
                self.program[-1] = bytechar + self.byte_add(self.program[-1][1:4], 1)
            else:
                self.program.append(bytechar)

        with open(out, "wb") as _r:
            for b in self.program:
                _r.write(b)
