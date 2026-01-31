module register_file(   
    input logic clk,
    input logic reset,
    input logic RegWrite,
    input logic [4:0] rs1,
    input logic [4:0] rs2,
    input logic [4:0] rd,
    input logic [31:0] wd,
    output logic [31:0] rd1,
    output logic [31:0] rd2,
);
    logic [31:0] r_out [31:0]; // Register Array
    logic [31:0] we;

    genvar k;
    generate 
        for (k = 0, k < 32; k++) begin : GEN_REGS
            assign we[k] = Register && (rd == k[4:0]) && (k != 0);

            register u_reg(
                .clk(clk),
                .reset(reset),
                .RegWrite(we[k]),
                .in(wd),
                .out(r_out[k])
            );
        end
    endgenerate

    assign rd1 = (rs1 == 0) ? 32'd0 : r_out[rs1];
    assign rd2 = (rs2 == 0) ? 32'd0 : r_out[rs2];
endmodule


module register( //32-bit register
    input logic clk, 
    input logic reset, 
    input logic RegWrite, 
    input logic [31:0] in, 
    output logic [31:0] out
);
    always_ff @(posedge clk) begin // keep sync reset
        if (reset)
            out <= 32'b0; 
        else if (RegWrite)
            out <= in;
    end
endmodule