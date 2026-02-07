module amp (input logic clk, 
            input logic reset,
            output logic [31:0] result); 
    // top-level module
   
    // PC register
    logic [31:0] PCNext;
    logic [31:0] PCout;
    register pc(
        .clk(clk), 
        .reset(reset), 
        .enable(PCwrite),
        .in(PCNext),
        .out(PCout)
    )

    logic [31:0] Adr;
    2to1mux pc_2to1_mux(
        .mx(AdrSrc),
        .a(PCout),
        .b(Result),
        .out(Adr)
    );
    
    // Instruction Memory
    logic [31:0] Instr;
    ram IMEM() // instruction memory - this is read only


    // Data Memory
    ram DMEM() // data memory

    // Register File
    logic [31:0] rd1;
    logic [31:0] rd2;
    logic [31:0] A;
    logic [31:0] WriteData;
    
    register_file u_register_file(
        .clk(clk),
        .reset(reset),
        .RegWrite(RegWrite),
        .rs1(Instr[19:15]),
        .rs2(Instr[24:20]),
        .rd(Instr{11:7}),
        .wd(Result),
        .rd1(rd1),
        .rd2(rd2),
    );  

    register rd1_register(
        .clk(clk), 
        .reset(reset), 
        .enable(1'b1),
        .in(rd1),
        .out(A)
    )

     register rd2_register(
        .clk(clk), 
        .reset(reset), 
        .enable(1'b1),
        .in(rd2),
        .out(WriteData)
    )

    // Src A Mux
    logic [31:0] SrcA;

    // Src B Mux
    logic [31:0] SrcB;

    // ALU
    logic [31:0] ALUResult;
    ALU alu_instance(
        .a(SrcA),
        .b(SrcB),
        .ALUctrl(ALUControl),
        .ALUout(ALUResult)
    );

    // Result
    logic [31:0] ALUOut;
    logic [31:0] Result;
    register u_reg (
        .clk(clk),
        .reset(reset),
        .RegWrite(1'b1),
        .in(ALUResult),
        .out(ALUOut)
    );

    4to1mux result_mux (
        .mx(ResultSrc)
        .a(ALUOut)
        .b(Data)
        .c(ALUResult)
        .d(32'd0)
        .out(Result)
    );

    // Control Unit FSM
    logic PCwrite; 
    logic AdrSrc;
    logic MemWrite;
    logic IRWrite;
    logic [1:0] ResultSrc;
    logic [3:0] ALUControl;
    logic [1:0] ALUSrcB;
    logic [1:0] AlUSrcA;
    logic [1:0] ImmSrc;
    logic RegWrite;

    FSM fsm_instance(
        

    )

endmodule