module ram #( // 1k x 4B ram block
    parameter DEPTH = 1024, 
    parameter WIDTH = 32
) 
(
    input clk, 
    input logic write_enable, 
    input logic [WIDTH-1:0]data_in,
    input logic [$clog2(DEPTH)-1:0]addr, // so for 1024, it's addr[9:0]
    output logic [WIDTH-1:0]data_out
);

logic [WIDTH-1:0] mem [0:DEPTH-1];

always_ff @(posedge clk) begin
    if(write_enable)
        mem[addr] <=data_in; 
    data_out <= mem[addr]; 
end

endmodule