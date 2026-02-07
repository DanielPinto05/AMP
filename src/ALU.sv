import alu_defs::*
module ALU ( 
    input logic [31:0] a, 
    input logic [31:0] b, 
    input logic [3:0] ALUctrl, 
    output logic [31:0] ALUout  
);
    // * ALU Mapping
    // 0 - ADD
    // 1 - SUB
    // 2 - Left Shift Logical Operation
    // 3 - Right Shift Arithmetic
    // 4 - Right Shift Logical
    // 5 - Bitwise OR
    // 6 - bitwise XOR
    // 7 - Signed set less than
    // 8 - Unsigned set less than 
    // 9 - AND
    always_comb begin
        case(ALUctrl)
            OP_ADD: ALUout = a + b;
            OP_SUB: ALUout = a - b;
            OP_SLL: ALUout = a << b[4:0];
            OP_SRA: ALUout = a >>> b[4:0];
            OP_SRL: ALUout = a >> b[4:0];
            OP_OR: ALUout = a | b;
            OP_XOR: ALUout = a ^ b;
            OP_SSLT: ALUout = ($signed(a) < $signed(b)) ? 1 : 0;
            OP_USLT: ALUout = (a < b) ? 1 : 0;
            OP_AND: ALUout = a & b;
            default: ALUout = 0;
        endcase
    end

endmodule
