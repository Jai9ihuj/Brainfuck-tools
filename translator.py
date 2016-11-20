#!/usr/bin/python3

import string

header_template = string.Template("""#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define L while (*pointer != 0) {
#define E }
#define R if (!read_cell(pointer)) {return false;}
#define W if (!write_cell(pointer)) {return false;}
#define D --*pointer;
#define I ++*pointer;
#define P if (pointer == memory) {return false;} --pointer;
#define N if (pointer == last) {return false;} ++pointer;

static bool read_cell(uint8_t *cell);
static bool write_cell(const uint8_t *cell);

#define MEMORY_LENGTH $memory_length
""")

execute_template = string.Template("""
static uint8_t memory[MEMORY_LENGTH];
static uint8_t *last = memory + MEMORY_LENGTH - 1;
static uint8_t *pointer = memory;

static bool execute(void) {$translated
	return true;
}
""")

execute_dumpable_template = string.Template("""#define LAST_POSITION $last_position

size_t position;
uint8_t memory[MEMORY_LENGTH];
uint8_t *last = memory + MEMORY_LENGTH - 1;
uint8_t *pointer = memory;

static bool execute(void) {
	switch (position) {$translated
	}

	return true;
}
""")

initialize_template = string.Template("""
	if (!error && argc != 1) {
		if (!error) {
			error = argc != 3;
		}

		FILE *numbers_file;

		if (!error) {
			numbers_file = fopen(argv[1], "r");

			error = numbers_file == NULL;
		}

		size_t shift;

		if (!error) {
			error = fscanf(numbers_file, "%zu %zu", &position, &shift) != 2;

			fclose(numbers_file);
		}

		if (!error) {
			error = (
				position > LAST_POSITION ||
				shift >= MEMORY_LENGTH
			);
		}

		FILE *memory_file;

		if (!error) {
			pointer += shift;

			memory_file = fopen(argv[2], "rb");

			error = memory_file == NULL;
		}

		if (!error) {
			fread(memory, 1, MEMORY_LENGTH, memory_file);
			fgetc(memory_file);

			error = (
				ferror(memory_file) != 0 ||
				feof(memory_file) == 0
			);
		}
	}
""")

main_template = string.Template("""
#ifndef __linux
	#error "Linux required"
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <unistd.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>

static bool read_cell(uint8_t *cell) {
	return syscall(SYS_read, 0, cell, 1) == 1;
}

static bool write_cell(const uint8_t *cell) {
	return syscall(SYS_write, 1, cell, 1) == 1;
}

int main(int argc, char **argv) {
	bool error = false;
$initialize
	if (!error) {
		error = fclose(stderr) != 0;
	}

	if (!error) {
		error = syscall(SYS_prctl, PR_SET_SECCOMP, SECCOMP_MODE_STRICT) != 0;
	}

	if (!error) {
		error = !execute();
	}

	syscall(SYS_exit, error ? EXIT_FAILURE : EXIT_SUCCESS);
}
""")

main_no_seccomp_template = string.Template("""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static bool read_cell(uint8_t *cell) {
	return fread(cell, 1, 1, stdin) == 1;
}

static bool write_cell(const uint8_t *cell) {
	return fwrite(cell, 1, 1, stdout) == 1;
}

int main(int argc, char **argv) {
	bool error = false;
$initialize
	if (!error) {
		error = !execute();
	}

	return error ? EXIT_FAILURE : EXIT_SUCCESS;
}
""")

def translate(instructions, memory_length, dumpable = False):
	translated = ""
	line_length = 0
	new_line = "\n\t"

	def append_translated(statement):
		nonlocal translated, line_length

		appended = (new_line if line_length == 0 else " ") + statement
		translated += appended
		line_length += len(appended)

		if line_length > 62 - len(new_line):
			line_length = 0

	if dumpable:
		new_line += "\t"
		append_translated("case 0: position = 0;")

		position = 0

		for i in instructions:
			if i in "RW":
				position += 1

				line_length = 0
				append_translated("case {0:}: position = {0:};".format(position))

			append_translated(i)

		execute = execute_dumpable_template.substitute(
			last_position = position,
			translated = translated
		)
	else:
		for i in instructions:
			append_translated(i)

		if len(instructions) != 0:
			translated += "\n"

		execute = execute_template.substitute(translated = translated)

	return header_template.substitute(memory_length = memory_length) + execute

if __name__ == "__main__":
	import argparse
	import sys

	argument_parser = argparse.ArgumentParser()

	argument_parser.add_argument("--maximum-code-length", "-c", type = int, default = 2 ** 20)
	argument_parser.add_argument("--maximum-loop-depth", "-l", type = int, default = 125)
	argument_parser.add_argument("--memory-length", "-m", type = int, default = 2 ** 20)
	argument_parser.add_argument("--no-seccomp", "-n", action = "store_true")
	argument_parser.add_argument("--dumpable", "-d", action = "store_true")
	argument_parser.add_argument("code", type = str)

	arguments = argument_parser.parse_args()

	if arguments.maximum_code_length < 0:
		raise Exception("Invalid maximum code length")

	if arguments.maximum_loop_depth < 0:
		raise Exception("Invalid maximum loop depth")

	if arguments.memory_length < 1:
		raise Exception("Invalid memory length")

	import interpreter

	with open(arguments.code, "r") as file:
		instructions, loops, IOs = interpreter.parse(file, arguments.maximum_code_length, arguments.maximum_loop_depth)

	sys.stdout.write(
		translate(instructions, arguments.memory_length, arguments.dumpable) +
		(main_no_seccomp_template if arguments.no_seccomp else main_template).substitute(
			initialize = initialize_template.substitute() if arguments.dumpable else ""
		)
	)
