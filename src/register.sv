module register( //32-bit register
    input logic clk, 
    input logic reset, 
    input logic enable, 
    input logic in[31:0], 
    output logic out[31:0]
)
    always_ff @(posedge clk or posedge reset) begin
        if (reset)
            out<=32'b0; 
        else if (enable)
            out <=in;
    end
endmodule