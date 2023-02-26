import sys
import os
import re

if len(sys.argv) == 1:
    raise ValueError("Usage: python interpreter.py <filename>")

filename = sys.argv[1]

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
