package alu_defs;
    localparam logic [3:0] OP_ADD  = 4'b0000;
    localparam logic [3:0] OP_SUB  = 4'b0001;
    localparam logic [3:0] OP_SLL  = 4'b0010;
    localparam logic [3:0] OP_SRA  = 4'b0011;
    localparam logic [3:0] OP_SRL  = 4'b0100;
    localparam logic [3:0] OP_OR   = 4'b0101;
    localparam logic [3:0] OP_XOR  = 4'b0110;
    localparam logic [3:0] OP_SSLT  = 4'b0111;
    localparam logic [3:0] OP_USLT = 4'b1000;
    localparam logic [3:0] OP_AND  = 4'b1001;
endpackage