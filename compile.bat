@echo off
nasm -fwin32 %1.asm -o %1.obj
gcc %1.obj -o %1.exe
del test.obj