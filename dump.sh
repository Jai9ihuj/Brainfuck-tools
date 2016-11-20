#!/bin/bash

rm -f numbers.txt memory.bin

gdb -p $1 -batch \
	-ex "set logging file numbers.txt" \
	-ex "set logging on" \
	-ex "printf \"%llu\\n%llu\\n\", position, pointer - (unsigned long long) &memory" \
	-ex "set logging off" \
	-ex "set max-value-size unlimited" \
	-ex "append memory memory.bin &memory last" \
	-ex "detach"
