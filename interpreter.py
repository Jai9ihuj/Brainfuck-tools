#!/usr/bin/python3

def parse(code_file, maximum_code_length, maximum_loop_depth = None):
	instructions = []
	loops = {}
	IOs = []

	stack = []

	for i in range(maximum_code_length):
		i = code_file.read(1)

		if len(i) != 1:
			break

		if i == "[":
			stack.append(len(instructions))

			if maximum_loop_depth is not None and len(stack) > maximum_loop_depth:
				raise Exception("Too deep loop")
		elif i == "]":
			if len(stack) == 0:
				raise Exception("Unexpected right bracket")

			loops[stack.pop()] = len(instructions)
		elif i in ",.":
			IOs.append(len(instructions))

		instruction = {
			"[": "L",
			"]": "E",
			",": "R",
			".": "W",
			"-": "D",
			"+": "I",
			"<": "P",
			">": "N"
		}.get(i)

		if instruction is not None:
			instructions.append(instruction)
	else:
		if len(code_file.read(1)) != 0:
			raise Exception("Too much code")

	if len(stack) != 0:
		raise Exception("Unbalanced brackets")

	return instructions, loops, IOs

def interpret(instructions, loops, memory, read = None, write = None):
	pointer = 0
	position = 0

	stack = []

	while position < len(instructions):
		instruction = instructions[position]

		if instruction == "E":
			position = stack.pop()
		else:
			if instruction == "L":
				if memory[pointer] == 0:
					position = loops[position]
				else:
					stack.append(position)
			elif instruction == "R":
				memory[pointer] = read()
			elif instruction == "W":
				write(memory[pointer])
			elif instruction == "D":
				memory[pointer] = (memory[pointer] - 1) % 256
			elif instruction == "I":
				memory[pointer] = (memory[pointer] + 1) % 256
			elif instruction == "P":
				if pointer == 0:
					raise Exception("Too left")

				pointer -= 1
			elif instruction == "N":
				if pointer == len(memory) - 1:
					raise Exception("Too right")

				pointer += 1

			position += 1

	return pointer

if __name__ == "__main__":
	import argparse
	import sys

	argument_parser = argparse.ArgumentParser()

	argument_parser.add_argument("--maximum-code-length", "-c", type = int, default = 2 ** 20)
	argument_parser.add_argument("--memory-length", "-m", type = int, default = 2 ** 20)
	argument_parser.add_argument("code", type = str)

	arguments = argument_parser.parse_args()

	if arguments.maximum_code_length < 0:
		raise Exception("Invalid maximum code length")

	if arguments.memory_length < 1:
		raise Exception("Invalid memory length")

	with open(arguments.code, "r") as file:
		instructions, loops, IOs = parse(file, arguments.maximum_code_length)

	memory = bytearray(arguments.memory_length)

	def read():
		byte = sys.stdin.buffer.read(1)

		if len(byte) != 1:
			raise Exception("Input error")

		return byte[0]

	def write(byte):
		if sys.stdout.buffer.write(bytes([byte])) != 1:
			raise Exception("Output error")

		sys.stdout.flush()

	interpret(instructions, loops, memory, read, write)
