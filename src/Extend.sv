module Extend( // extend immediates to 32-bits depending on what ImmSrc gives you
    input logic [2:0] ImmSrc, 
    input logic [31:7] instr, // the actual instruction from IR
    output logic [31:0] ImmExt
);

/* five different extensions are needed. Note that all (except U-type) are sign-extended
000: I-type extend
001: S-type
010: B-type
011: U-type - load upper immediate - 20 bits go directly to upper 20 bits of a reg
100: J-type
*/

parameter I=3'b000, S = 3'b001, B = 3'b010, U = 3'b011, J = 3'b100;

always_comb begin
    case (ImmSrc)
        I: ImmExt = {{20{instr[31]}}, instr[31:20]};
        S: ImmExt = {{20{instr[31]}}, instr[31:25], instr[11:7]};
        B: ImmExt = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
        U: ImmExt = {{instr[31:12]}, 12'b0};
        J: ImmExt = {{12{instr[31]}}, instr[31], instr[19:12], instr[20], instr[30:21], 1'b0};
        default: ImmExt = 32'b0; //! is this is a bad idea?
    endcase
    
end


endmodule