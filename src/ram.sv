module ram #( // 1k x 4B ram block
    parameter DEPTH = 1024, 
    parameter WIDTH = 32, 
) (
    input clk, 
    input write_enable, 
    input write_data[WIDTH-1:0],
    input addr[$clog2(DEPTH)-1:0], // so for 1024, it's addr[9:0]
    output read_data[WIDTH-1:0]
)

logic [WIDTH-1:0] mem [0:DEPTH-1];

always_ff @(posedge clk) begin
    if(write_enable)
        mem[addr] <=write_data; 
    read_data <= mem[addr]; 
end

endmodule