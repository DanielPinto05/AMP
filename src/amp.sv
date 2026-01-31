module amp() 
// top-level module
logic clk; 
logic reset; 
logic PCwrite; 




register pc(
    .clk(clk), 
    .reset(reset), 
    .enable(PCwrite), 
    .)


ram IMEM() // instruction memory - this is read only

ram DMEM() // data memory


endmodule