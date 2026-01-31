module ALU ( 
    input a[31:0], 
    input b[31:0], 
    input ALUctrl[3:0], 
    output ALUout[31:0];  
)
    // * ALU Mapping
    // 0 - Adding
    // 1 - Subtracting
    // 2 - Left Shift Logical Operation
    // 3 - Right Shift Arithmetic
    // 4 - Right Shift Logical
    // 5 - 
    
    always_comb begin
        case(ALUOP)
            0: ALUout = a + b;
            1: ALUout = a - b;
            2: ALUout = a << b[4:0];
            3: ALUout = a >>> b[4:0];
            4: ALUout = a >> b[4:0];
            default: alu_out = 0;
        endcase
    end
    

endmodule
