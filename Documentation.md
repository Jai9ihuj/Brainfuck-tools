Brainfuck tools
===============

Brainfuck interpreter and translator into C.

It supports the [standard](http://www.muppetlabs.com/~breadbox/bf/standards.html) Brainfuck with the following implementation defined details:
- a cell is an 8-bit unsigned integer;
- the memory size is defined by the user;
- moving out of the memory causes termination;
- increment of 255 results in 0, decrement of 0 is 255;
- terminates on EOF;
- returns an error on unbalanced brackets.

Interpreter
-----------

Requires a sourse file name and supports two command line options:
- `--maximum-code-length`, `-c` - the maximum accepted code file size in bytes, defaults to 1 MiB;
- `--memory-length`, `-m` - the memory buffer length in bytes, defaults to 1 MiB.

Translator
----------

Requires a sourse file name and writes the result to the standard output, supports the same command line options as the interpreter and several additional:
- `--maximum-loop-depth`, `-l` - the maximum allowed loop depth, defaults to 125 (127 block levels, guaranteed by the C standard, minus 2 for the function and possible `switch`);
- `--maximum-io-instructions`, `-i` - the maximum number of IO instructions, works only with `--dumpable`. Defaults to 1022 (1023 guaranteed switch cases minus 1 for one not IO case);
- `--no-seccomp`, `-n` - don't use `seccomp`;
- `--dumpable`, `-d` - see the next section.

Unless the `--no-seccomp` option is specified, the translated programm must be compiled with the GNU C extensions.

Dump
----

The internal state of a Brainfuck programm consists of four elements:
- the code;
- the current instruction position;
- the memory;
- the current memory pointer.

The first is constant, the other three can be extracted from a programm with a debugger.

To make a programm dumpable, translate it with the `--dumpable` option and compile with `-g`. The programm can be dumped only when it's blocked for IO.

The `dump.sh` script requires a process's ID:

```
$ sudo ./dump.sh 1328
```

It creates two files: `numbers.txt` and `memory.bin`. The first contains the current IO operation number and memory pointer, the second is the memory dump.

To restore the internal state, run the programm again, passing the generated files as command line arguments:

```
$ ./a.out numbers.txt memory.bin
```
