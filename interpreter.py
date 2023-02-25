import sys
import os

if len(sys.argv) == 1:
    raise ValueError("Usage: python interpreter.py <filename>")

filename = sys.argv[1]

if not os.path.exists(filename):
    raise FileNotFoundError(f"File {filename} not found")

with open(filename, "r") as f:
    program = f.read().replace("\n", "").replace(" ", "") + " "

jump_points = {}
next_points = {}

for i in range(len(program)):
    checked_i = False
    if program[i] != "헤":
        continue
    for j in range(1, len(program)+1):
        if program[-j] == "힝":
            jump_points[len(program)-j] = i
            next_points[i] = len(program)-j
            checked_i = True
            break
    if not checked_i:
        raise ValueError("헤 without 힝")


pointer = 0
memory = {}
cursor = 0

while cursor < len(program):
    char = program[cursor]
    if char == " ":
        break
    if char not in "?!냥뀨.,헤힝":
        raise ValueError(f"Invalid character {char}")
    match char:
        case "?":
            pointer += 1
        case "!":
            pointer -= 1
        case "냥":
            memory[pointer] = memory.get(pointer, 0) + 1
        case "뀨":
            memory[pointer] = memory.get(pointer, 0) - 1
        case ".":
            print(chr(memory.get(pointer, 0)), end="")
        case ",":
            memory[pointer] = pointer
        case "헤":
            if memory.get(pointer, 0) == 0:
                cursor = next_points[cursor]
        case "힝":
            if memory.get(pointer, 0) != 0:
                cursor = jump_points[cursor]

    cursor += 1