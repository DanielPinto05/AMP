module amp() 
// top-level module
logic clk; 
logic reset; 
logic PCwrite; 




register pc(
    .clk(clk), 
    .reset(reset), 
    .enable())



endmodule