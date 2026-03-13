import alu_defs::*; // imports all parameters from alu_defs.sv

module FSM(
    input logic clk,
    input logic [6:0] op,  // operation
    input logic funct7_5, // 
    input logic [2:0] funct3,
    input logic reset, 
    output logic PCWrite, 
    output logic AdrSrc, //mux signal
    output logic MemWrite,
    output logic IRWrite, 
    output logic [1:0] ResultSrc, // takes output of ALUout reg
    output logic [3:0]ALUControl, 
    output logic [1:0] ALUSrcA,
    output logic [1:0] ALUSrcB,
    output logic [1:0] ImmSrc,
    output logic RegWrite
);

// defines the state_t type and what values it can take on.
typedef enum logic[3:0] {
    RESET, FETCH, DECODE, MEMADR, EXECUTER, EXECUTEI, BRANCH, JAL, LUI, MEMREAD, MEMWB, MEMWRITE, ALUWB
} state_t; 

state_t state, next_state; 

/*registers*/
always_ff @(posedge clk) begin
if (reset)
    state = RESET;
else 
    state <= next_state; 

end

/*compute next state based on current + opcodes*/
//! note that ONLY lw/sw is implemented for now. Next step is lb, lh, lhu
always_comb begin
    next_state = state; //* hold state if next_state doesn't get assigned
    case(state)
        RESET: next_state = FETCH; 
        FETCH: next_state = DECODE; 
        DECODE: 
            begin unique casez(op) //  QUES: Why use casez?
                3: next_state = MEMADR; //lw
                35: next_state = MEMADR; //sw
                51: next_state = EXECUTER; //R-type
                19: next_state = EXECUTEI; //I-tpye
                99: next_state = BRANCH; 
                111: next_state = JAL; 
                23: next_state = LUI; 
                default: next_state = RESET;
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
    RESET: begin
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 0; //* ready to receive data from mem
        ResultSrc = X; 
        ALUSrcA = X; 
        ALUSrcB = X; 
        ImmSrc = X; 
        RegWrite = 0; 
    end
    FETCH: begin
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 1; //* ready to receive data from mem
        ResultSrc = X; 
        ALUSrcA = X; 
        ALUSrcB = X; 
        ImmSrc = X; 
        RegWrite = 0; 
    end
    DECODE: begin
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 0; //* ready to receive data from mem
        ResultSrc = X; 
        ALUSrcA = X; 
        ALUSrcB = X; 
        ImmSrc = X; 
        RegWrite = 0; 
    end
    EXECUTEI: begin
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 1; //* ready to receive data from mem
        ResultSrc = X; 
        ALUSrcA = X; 
        ALUSrcB = X; 
        ImmSrc = X; 
        RegWrite = 0; 
    end
    EXECUTER: begin 
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 1; //* ready to receive data from mem
        ResultSrc = X; 
        ALUSrcA = 2'b10; 
        ALUSrcB = 2'b00; 
        ImmSrc = X; 
        RegWrite = 0; 
    end
    ALUWB: begin
        PCWrite = 0; 
        AdrSrc = 0; 
        MemWrite = 0; 
        IRWrite = 1; //* ready to receive data from mem
        ResultSrc = 2'b10; 
        ALUSrcA = X; 
        ALUSrcB = X; 
        ImmSrc = X; 
        RegWrite = 1; 
    end
endcase
end

// AlU control
always_comb begin
    ALUControl = ALU_ADD; // default

    case (op)
        7'b0110011: begin // R-type
            case (funct3)
                3'b000: ALUControl = funct7_5 ? ALU_SUB : ALU_ADD;
                3'b111: ALUControl = ALU_AND;
                3'b110: ALUControl = ALU_OR;
                3'b100: ALUControl = ALU_XOR;
                3'b001: ALUControl = ALU_SLL;
                3'b101: ALUControl = funct7_5 ? ALU_SRA : ALU_SRL;
                3'b010: ALUControl = ALU_SSLT;
                3'b011: ALUControl = ALU_USLT;
                default: ALUControl = ALU_ADD;
            endcase
        end

        // 7'b0010011: begin // I-type ALU
        //     case (funct3)
        //         3'b000: ALUControl = ALU_ADD; // addi
        //         3'b111: ALUControl = ALU_AND; // andi
        //         3'b110: ALUControl = ALU_OR;  // ori
        //         3'b100: ALUControl = ALU_XOR; // xori
        //         3'b001: ALUControl = ALU_SLL; // slli
        //         3'b101: ALUControl = funct7_5 ? ALU_SRA : ALU_SRL; // srai/srli
        //         3'b010: ALUControl = ALU_SLT;  // slti
        //         3'b011: ALUControl = ALU_SLTU; // sltiu
        //         default: ALUControl = ALU_ADD;
        //     endcase
        // end

        // 7'b0000011, // loads
        // 7'b0100011, // stores
        // 7'b1100111: // jalr
        //     ALUControl = ALU_ADD; // address calc = base + imm

        // 7'b1100011: begin // branches
        //     // often you do SUB/compare here depending on datapath
        //     ALUControl = ALU_SUB;
        // end

        default: ALUControl = ALU_ADD;
    endcase
end

endmodule