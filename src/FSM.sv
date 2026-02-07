import alu_defs::*; // imports all parameters from alu_defs.sv

module FSM(
    input logic op[6:0], 
    input logic funct7_5; 
    input logic funct3[2:0]; 
    output logic PCWrite, 
    output logic AdrSrc, //mux signal
    output logic MemWrite,
    output logic IRWrite, 
    output logic ResultSrc[1:0], // takes output of ALUout reg
    output logic ALUControl[3:0], 
    output logic ALUSrcA[1:0],
    output logic ALUSrcB[1:0],
    output logic ImmSrc[1:0],
    output logic RegWrite,
);



endmodule