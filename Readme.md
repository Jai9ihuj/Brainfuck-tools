Brainfuck tools
===============

Brainfuck interpreter and translator into C.

See the [documentation](Documentation.md).

Features
--------

A translated programm checks memory boundaries and can sandbox itself using the [Seccomp](https://en.wikipedia.org/wiki/Seccomp) system call on Linux.

The internal state of a translated programm can be saved and restored later.
