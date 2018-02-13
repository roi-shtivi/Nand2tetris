// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/divide/Divide.asm

//The program input will be at R13,R14 while the result R13/R14 will be store at R15.
//The remainder should be discarded.
//You may assume both numbers are positive.
//The program should have a running time logarithmic with respect to the input.

@R13
D=M
@divident
M=D
@quotient
M=0
@currQuotientBase
M=1
@R14
D=M
@currentDev
M=D

(WHILE_CONDITION)
@divident
D=M
@R14
D=D-M
@WHILE
D;JGE //While(R13>=R14)
@UPDATE_ANSWER //(R13<R14)
D;JLT

(WHILE)
@divident
D=M
@currentDev
D=D-M 
@IF //(R13>=currDevisor)
D;JGE
@ELSE
D;JLT

(IF)
@currentDev
D=M
@divident
M=M-D //divident-=currDivisor
@currQuotientBase
D=M
@quotient
M=M+D //quotient+=currQuotientBase
@currentDev
M=M<< //currentDev*=2
@currQuotientBase
M=M<< // currQuotientBase*=2
@WHILE_CONDITION
0;JMP

(ELSE)
@currentDev
M=M>> //currentDev/=2
@currQuotientBase
M=M>> // currQuotientBase/=2
@WHILE_CONDITION
0;JMP

(UPDATE_ANSWER)
@quotient
D=M
@R15
M=D
@END
0;JMP

(END)
0;JMP

