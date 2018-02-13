// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

@R0
D=M
@n
M=D //n = R0
@i
M=1 //i =1
@R2
M=0 //result of mult

(LOOP)
@i
D=M
@n
D=D-M
@END
D;JGT // if i>n goto END

@R1
D=M
@R2
M=M+D // R2+=R1 
@i
M=M+1 //i++
@LOOP
0;JMP

(END)
@END
0;JMP

