`timescale 1ns/1ns

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
            0: ALUout = a + b;
            1: ALUout = a - b;
            2: ALUout = a << b[4:0];
            3: ALUout = a >>> b[4:0];
            4: ALUout = a >> b[4:0];
            5: ALUout = a | b;
            6: ALUout = a ^ b;
            7: ALUout = ($signed(a) < $signed(b)) ? 1 : 0;
            8: ALUout = (a < b) ? 1 : 0;
            9: ALUout = a & b;
            default: ALUout = 0;
        endcase
    end

endmodule
