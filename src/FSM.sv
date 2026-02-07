import alu_defs::*; // imports all parameters from alu_defs.sv

module FSM(
    input logic op[6:0], 
    input logic funct7_5,
    input logic funct3[2:0],
    input logic reset, 
    output logic PCWrite, 
    output logic AdrSrc, //mux signal
    output logic MemWrite,
    output logic IRWrite, 
    output logic ResultSrc[1:0], // takes output of ALUout reg
    output logic ALUControl[3:0], 
    output logic ALUSrcA[1:0],
    output logic ALUSrcB[1:0],
    output logic ImmSrc[1:0],
    output logic RegWrite,
);

// defines the state_t type and what values it can take on.
typedef enum logic[3:0] {
    RESET, FETCH, DECODE, MEMADR, EXECUTER, EXECUTEI, BRANCH, JAL, LUI, MEMREAD, MEMWB, MEMWRITE, ALUWB
} state_t; 

state_t state, next_state; 




/*registers*/
always_ff @(posedge clk) begin
if (reset) state = RESET;
else 
end

/*compute next state based on current + opcodes*/
//! note that ONLY lw/sw is implemented for now. Next step is lb, lh, lhu
always_comb begin
    next_state = state; //* hold state if next_state doesn't get assigned
    case(state)
        RESET: next_state = FETCH; 
        FETCH: next_state = DECODE; 
        DECODE: 
            begin unique casez(op)
                3: next_state = MEMADR; //lw
                35: next_state = MEMADR; //sw
                default: next_state = RESET;
                51: next_state = EXECUTER; //R-type
                19: next_state = EXECUTEI; //I-tpye
                99: next_state = BRANCH; 
                111: next_state = JAL; 
                23: next_state = LUI; 
            endcase
            end
        MEMADR: begin
            if (op==3)
                next_state = MEMREAD; // lw
            else if (op==35)
                next_state = MEMWRITE; // sw
            end
        MEMREAD: next_state = MEMWB; // writeback to registers
        MEMWB: next_state = FETCH; 
        MEMWRITE: next_state = FETCH; 
        EXECUTER: next_state = ALUWB; 
        EXECUTEI: next_state = ALUWB; 
        ALUWB: next_state = FETCH; 
        BRANCH: next_state = FETCH; 
        JAL: next_state = ALUWB; 
        LUI: next_state = ALUWB; 
        default: next_state = RESET; 
    endcase
end



always_comb begin
case(state)
RESET: 
    PCWrite = 0; 
    AdrSrc = 0; 
    MemWrite = 0; 
    IRWrite = 0; //* ready to receive data from mem
    ResultSrc = X; 
    ALUControl = X; 
    ALUSrcA = X; 
    ALUSrcB = X; 
    ImmSrc = X; 
    RegWrite = 0; 


FETCH:
    PCWrite = 0; 
    AdrSrc = 0; 
    MemWrite = 0; 
    IRWrite = 1; //* ready to receive data from mem
    ResultSrc = X; 
    ALUControl = X; 
    ALUSrcA = X; 
    ALUSrcB = X; 
    ImmSrc = X; 
    RegWrite = 0; 
endcase
end



endmodule