import collections
from pathlib import Path

class Communicator:
    """
    Communicator that allows communication between two :class:`NyanInterpreter` or :class:`NyanBinaryInterpreter`.\n
    Use **Communicator.send** to save data, **Communicator.receive** to take saved data.\n
    """
    nyan_a: NyanInterpreter | NyanBinaryInterpreter
    nyan_b: NyanInterpreter | NyanBinaryInterpreter
    a_to_b_fill: bool
    b_to_a_fill: bool
    a_to_b: int | None
    b_to_a: int | None
    def __init__(self, nyan_a, nyan_b):
        """
        :param NyanInterpreter or NyanBinaryInterpreter nyan_a: binary/normal interpreter to communicate with
        :param NyanInterpreter or NyanBinaryInterpreter nyan_b: binary/normal interpreter to communicate with
        :rtype: Communicator
        """
    def send(self, nyan, data):
        """
        Saves data to a_to_b or b_to_a, make a_to_b_fill or b_to_a_fill to True \n
        can be returned by **Communicator.receive**
        :param NyanInterpreter or NyanBinaryInterpreter nyan: binary/normal interpreter that sends data
        :param int data: will be saved to opposite interpreter's data container
        :rtype: None
        :raise ValueError: when invalid interpreter given
        """
    def receive(self, nyan):
        """
        Returns data from a_to_b or b_to_a, make a_to_b_fill or b_to_a_fill to False\n
        :param NyanInterpreter or NyanBinaryInterpreter nyan: binary/normal interpreter that receives data
        :return: int if saved data from opposite interpreter, None if no data to receive
        :rtype: int or None
        :raise ValueError: when invalid interpreter given
        """
    def get_nyan(self, nyan):
        """
        Returns opposite binary/normal interpreter or base interpreter
        :param NyanInterpreter or NyanBinaryInterpreter nyan: base binary/normal interpreter
        :return: opposite interpreter
        :rtype: NyanInterpreter
        :raise ValueError: when invalid interpreter given
        """


class Signals:
    """
    Set of CONSTANT signals used by communication between :class:`NyanEngine` and
    interpreters like :class:`NyanInterpreter` or :class:`NyanBinaryInterpreter`.

    .. note::
        - PAUSE = 0
        - MAIN_EOF = 2
        - SUB_EOF = 3
        - KEEP_GOING = 4
    """
    PAUSE: int
    MAIN_EOF: int
    SUB_EOF: int
    KEEP_GOING: int


class Pointer:
    """
    Pointer of interpreters like :class:`NyanInterpreter` or :class:`NyanBinaryInterpreter`.\n
    Used to point address of :class:`Memory`.
    """
    _v: int
    def __init__(self, initial=None):
        """
        :param int or None initial: initial value of pointer. Automatically set to 0 if nothing given.
        """

    def increase(self):
        """
        Increase pointing address by 1.
        :return:
        """

    def decrease(self):
        """
        Decrease pointing address by 1
        :return:
        """

    def set(self, value):
        """
        Set pointing address to :param:`value`
        :param int value:
        :return:
        """

    def get(self):
        """
        Get current pointing address
        :return: current pointing address
        :rtype: int
        """


class Memory:
    """
    Memory of interpreters like :class:`NyanInterpreter` or :class:`NyanBinaryInterpreter`.\n
    Used to store/withdraw values from memory via :class:`Pointer`
    """
    memory: dict
    def __init__(self, initial=None):
        """
        :param dict or None initial: initial dictionary of memory. Automatically set to 0 if nothing given.
        """

    def increase(self, pointer):
        """
        Increase value in given pointer's address
        :param Pointer pointer:
        :return:
        """

    def decrease(self, pointer):
        """
        Decrease value in given pointer's address
        :param Pointer pointer:
        """

    def set(self, pointer: Pointer, value: int):
        """
        Set value in given pointer's address
        :param Pointer pointer:
        :param int value:
        """

    def get(self, pointer: Pointer):
        """
        Get value from given pointer's address
        :param Pointer pointer:
        :rtype: int
        :return: :class:`int` if value set. if value is not even touched, returns **0**.
        """


class ProgramParser:
    """
    Parser for Nyanlang source code.\n
    Accepting only text file (.nyan), not binary file (.nya).\n
    Check if given path is not exists, if file suffix is not valid, and parse program.
    """
    filename: Path
    program: str | None
    def __init__(self, filename: Path):
        """
        :param Path filename:
        """

    def parse(self):
        """
        Parse program with path exists check, suffix check.\n
        Once it gets file data, it removes all comments, newline, spaces.\n
        To make EOF signal, it automatically appends space at the end.
        :rtype str:
        :return: properly parsed program source
        :raises FileNotFoundError: if file is not exists
        :raises ValueError: if file extension is not valid
        """


class NyanInterpreter:
    """
    General interpreter for running one Nyanlang source code.\n
    If mouse support is required, use :class:`NyanEngine` or :class:`NyanBinaryEngine`.\n
    """
    filename: Path
    initialized: bool

    program: str | None
    debug: bool
    sub: bool

    cursor: int
    memory: Memory
    pointer: Pointer
    module_pointer: Pointer
    pointing_parents: bool
    children: dict[int, Communicator]
    parents: dict[int, Communicator]

    jump_points: dict[int, int]
    next_points: dict[int, int]

    keywords: dict[str, collections.Callable[[NyanInterpreter], None | tuple[int, bool, int]]]

    def __init__(self, filename, subprocess=False, debug=False):
        """
        :param Path filename:
        :param bool subprocess:
        :param bool debug:
        """

    def init(self):
        """
        Initialize interpreter.\n
        It will do:
         + parse program
         + parse loop points from parsed program
         + set `self.initialized` to true
         + return self
        since it returns self, you can chain this function call with `self.run()`.\n
        Example:
          NyanInterpreter(Path(".").absolute()).init().run()

        :rtype: NyanInterpreter
        """

    def reset(self):
        """
        Reset interpreter runtime attributes.\n
        It will do:
         + set `self.cursor` to 0
         + set `self.memory` to new :class:`Memory` object.
         + set `self.pointer` and `self.module_pointer` to new :class:`Pointer` object.
         + set `self.pointing_parents` to False.
        :return:
        """

    def add_keyword(self, keyword: str) -> collections.Callable[[collections.Callable[[NyanInterpreter], any]], None]:
        """
        Function decorator for adding a keyword. \n
        You can use this function after making an instance of :class:`NyanInterpreter`.\n
        >>> nyan = NyanInterpreter(Path("."))
        >>> @nyan.add_keyword("w")
        ... def w_handler(o: NyanInterpreter):
        ...     ...
        :param keyword: a character that will be registered as keyword.
        """
        def wrapper(handler: collections.Callable[[NyanInterpreter], any]):
            """
            :param handler: A handler function that will take NyanInterpreter object, and handle keyword event.
            """

    def add_parent(self, parent, pos):
        """
        Add :class:`Communicator` between parent and self.
        :param Communicator parent:
        :param int pos:
        :raises ValueError: when same parent communicator already added
        """

    def add_child(self, child, pos):
        """
        Add :class:`Communicator` between child and self.
        :param Communicator child:
        :param int pos:
        :raises ValueError: when same child communicator already added
        """

    def parse_program(self):
        """
        Parse program using :class:`ProgramParser` and set `self.program` from parse result.
        """

    def parse_loop_points(self):
        """
        Parse loop points from parsed program (self.program).
        """
        def _find_match(start_pair):
            """
            Find matching loop ending keyword pair of loop starting keyword.
            :param int start_pair: Index of starting pair
            :raises SyntaxError: if there is no matching pair
            """

    def before_run(self):
        ...

    def after_run(self):
        ...

    def start_of_loop(self):
        ...

    def end_of_loop(self):
        ...

    def module_read(self, keyword=":"):
        """
        Register handler for module reading keyword.
        :param str keyword:
        """
        def wrapper(o) -> tuple[int, bool, int] | None:
            """
            Handler for module reading keyword.
            :param NyanInterpreter o:
            :raises ValueError: if parent cat or child cat does not exist
            """

    def module_write(self, keyword=";"):
        """
        Register handler for module writing keyword.
        :param str keyword: 
        """
        def wrapper(o) -> tuple[int, bool, int]:
            """
            Handler for module writing keyword.
            :param NyanInterpreter o:
            :raises ValueError: if parent cat or child cat does not exist
            """

    def jumper_start(self, keyword="~"):
        """
        Register handler for jumper start keyword.
        :param str keyword:
        """
        def wrapper(o):
            """
            Handler for jumper start keyword.
            :param NyanInterpreter o:
            :return:
            """

    def jumper_end(self, keyword="-"):
        """
        Register handler for jumper end keyword.
        :param str keyword:
        """
        def wrapper(o):
            """
            Handler for jumper end keyword.
            :param NyanInterpreter o:
            :return:
            """

    def module_control(self, keyword="'"):
        """
        Register handler for module control keyword.
        :param str keyword:
        """
        def wrapper(o):
            """
            Handler for module control keyword.
            :param NyanInterpreter o:
            """

    def run(self) -> tuple[int, bool, int]:
        """
        Run interpreter's program with current runtime variables.
        :raises SyntaxError: when invalid character(keyword) detected
        """


class NyanBinaryInterpreter(NyanInterpreter):
    """
    NyanInterpreter, but handles binary code.
    """
    program: bytes | None
    constant_program: bytes | None
    keywords: dict[bytes, collections.Callable[[NyanBinaryInterpreter], None | tuple[int, bool, int]]]
    def __init__(self, filename, subprocess=False, debug=False):
        """
        :param Path filename:
        :param bool subprocess:
        :param bool debug:
        """

    def add_binary_keyword(self, keyword: bytes):
        """
        Function decorator for adding a keyword. \n
        You can use this function after making an instance of :class:`NyanBinaryInterpreter`.\n
        >>> nyan = NyanBinaryInterpreter(Path("."))
        >>> @nyan.add_keyword("w")
        ... def w_handler(o: NyanBinaryInterpreter):
        ...     ...
        :param keyword: a character that will be registered as keyword.
        """
        def wrapper(handler: collections.Callable[[NyanBinaryInterpreter], any]):
            """
            :param handler: A handler function that will take NyanBinaryInterpreter object, and handle keyword event.
            """

    def parse_program(self):
        """
        Parse program with path exists check, suffix check.\n
        Once it gets file data, it removes all comments, newline, spaces.
        :raises FileNotFoundError: if file is not exists
        :raises ValueError: if file extension is not valid
        """

    def parse_loop_points(self):
        """
        Parse loop points from parsed program (self.program).
        """
        def _find_match(start_pair):
            """
            Find matching loop ending keyword pair of loop starting keyword.
            :param int start_pair: Index of starting pair
            :raises SyntaxError: if there is no matching pair
            """

    def run(self) -> tuple[int, bool, int]:
        """
        Run interpreter's program with current runtime variables.
        """


class NyanEngine:
    """
    Engine for managing tree of interpreters, helping communications between interpreters.
    """
    debug: bool
    root: NyanInterpreter | NyanBinaryInterpreter
    nodetree: list[NyanInterpreter | NyanBinaryInterpreter]
    references: dict[Path, NyanInterpreter | NyanBinaryInterpreter]
    nyans: list[NyanInterpreter | NyanBinaryInterpreter]
    def __init__(self, root_name, *, debug=False):
        """
        :param Path root_name: path of root interpreter's source code
        :keyword debug:
        """

    def read_mouse(self, path: str | Path) -> collections.Generator[tuple[int, int, str], None, None]:
        """
        Read mouse information from given path
        :param path:
        :raises SyntaxError: when invalid mouse info detected
        """

    def mouse_exists(self, nyan: NyanInterpreter | None = None) -> str:
        """
        :param nyan:
        :return: mouse path if path exist, blank string ("") if not exist.
        """

    def find_mouse_info(self, nyan: NyanInterpreter | None = None) -> None:
        """
        Create/Register all child/parent interpreter relationsheep with communicator
        :param nyan:
        """

    def read_binary_mouse(self, data) -> collections.Generator[tuple[int, int, str], None, None]:
        """
        Read binary mouse information from given data
        :param bytes data:
        """

    def binary_mouse_exists(self, data) -> bool:
        """
        :param bytes data:
        :return: True if mouse data exist, False if not exist.
        """

    def find_binary_mouse_info(self, nyan: NyanInterpreter | NyanBinaryInterpreter | None = None) -> None:
        """
        Create/Register all child/parent interpreter relationsheep with communicator
        :param nyan:
        """

    def run(self):
        """
        Run root interpreter, and follow signals.
        :return:
        """


class NyanBuilder(NyanEngine):
    keywords: dict[str, bytes]
    compress_target: bytes
    program: list[bytes]

    def __init__(self, root_name, *, debug=False):
        """
        :param str root_name:
        :keyword bool debug:
        """

    @staticmethod
    def byte_add(byte, count=1):
        """
        Add count to bytes
        :param bytes byte:
        :param int count:
        :return:
        """

    def find_mouse_info(self, nyan: NyanInterpreter | None = None) -> None:
        """
        Parse mouse info, add infos into program.
        :param nyan:
        """

    def build(self, output: str | None = None) -> None:
        """
        Build a binary file based on keyword-bytes dictionary.
        :param output:
        """
