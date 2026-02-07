module 2to1mux (
    input logic mx,
    input logic [31:0] a,
    input logic [31:0] b,
    output logic [31:0] out
);
    always_comb begin
        case(mx)
            0: out = a;
            1: out = b;
            default: out = 0;
        endcase
    end
endmodule

module 4to1mux (
    input logic [1:0] mx,
    input logic [31:0] a,
    input logic [31:0] b,
    input logic [31:0] c,
    input logic [31:0] d,
    output logic [31:0] out
);
    always_comb begin 
        case(mx)
            0: out = a;
            1: out = b;
            2: out = c;
            3: out = d;
            default: out = 0;
        endcase
    end
endmodule