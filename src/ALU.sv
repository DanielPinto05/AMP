module ALU (
    input clk, 
    input a[31:0], 
    input b[31:0], 
    input ALUctrl, // we'll extend this as we need more control signals. for now 0 is add. 
    output ALUout[31:0];  
)

    assign sum = a + b; 
    assign difference = a-b; 
    


endmodule