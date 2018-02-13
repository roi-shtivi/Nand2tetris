// This file is part of www.nand2tetris.org
// by Nisan and Schocken, MIT Press.
// File name: projects/04/sort.asm

//The program input will be at R14(starting address),R15(length of array).
//The program should sort the array starting at the address in R14 with length specified in R15.
//The sort is in descending order - the largest number at the head of the array.
//support negative numbers.

@i
M = 0 			// i = 0

(OUTTER)
@R14
D = M			// D = R14
@i
A = D + M		// A = R14 + i
D = A			// D = R14 + i
@swap1		// pointer to the i-th member of the array
M = D			// swap1 = R14 + i
@i
D = M			// D = i
@j
M = D + 1		// j = i + 1

(INNER)
@R15
D = M			// D = R15
@j
D = D - M		// D = R15 - j
@INEND
D;JLE			// if (j <= R15) goto INEND
@R14
D = M			// D = R14
@j
A = D + M		// A = R14 + j
D = A			// D = R14 + j
@swap2
M = D			// swap2 = R14 + j
@swap1
A = M			// A = swap1
D = M			// D = RAM[swap1]
@swap2
A = M			// A = swap2
D = D - M		// D = RAM[swap1] - RAM[swap2]
@SWAP
D;JLT			// if (RAM[swap2] > RAM[swap1]) goto SWAP

(AFTERSWAP)
@R15
D = M			// D = R15
@j
M = M + 1		// j++
D = D - M		// D = R15 - j
@INNER
D;JGT			// if (j < R15) goto INNER
@INEND
0;JMP			// else
(SWAP)
@swap2
A = M			// A = swap2
D = M			// D = RAM[swap2]
@temp
M = D			// temp = RAM[swap2]
@swap1
A = M 			// A = swap1
D = M			// D = RAM[swap1]
@swap2
A = M 			// A = swap2
M = D			// RAM[swap2] = RAM[swap1]  (swap)

@temp
D = M			// D = temp
@swap1
A = M			// A = swap1
M = D			// RAM[swap1] = temp
@AFTERSWAP
0;JMP

(INEND)
@i
M = M + 1		// i = i++
@R15
D = M			// D = R15
@i
D = D - M		// D = R15 - i
@OUTTER
D;JGT			// if (i < R15) goto OUTTER
(END)

