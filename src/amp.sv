module amp (input logic clk, 
            input logic reset,
            output logic [31:0] result); 
    // top-level module
   
    // PC register
    logic [31:0] PCNext;
    logic [31:0] PCout;
    logic [31:0] OldPC;
    
    register pc_instance(
        .clk(clk), 
        .reset(reset), 
        .enable(PCwrite),
        .in(PCNext),
        .out(PCout)
    );

    register old_pc_instance(
        .clk(clk), 
        .reset(reset), 
        .enable(1),
        .in(PCout),
        .out(OldPC)
    );

    logic [31:0] Adr;
    two_one_mux pc_2to1_mux(
        .mx(AdrSrc),
        .a(PCout),
        .b(Result),
        .out(Adr)
    );
    
    // Instruction Memory
    logic [31:0] Instr;
    logic [31:0] intructData;

     ram #(
        .DEPTH(1024),
        .WIDTH(32)
    ) IMEM (
        .clk(clk),
        .write_enable(0), 
        .data_in(0),
        .addr(Adr[11:2]),
        .data_out(intructData)
    );

    register instruction_register(
        .clk(clk), 
        .reset(reset), 
        .enable(IRWrite),
        .in(ReadData),
        .out(Instr)
    );

    // Data Memory
    logic [32:0] ReadData;
    logic [32:0] Data;
      ram #(
        .DEPTH(1024),
        .WIDTH(32)
    ) DMEM (
        .clk(clk),
        .write_enable(MemWrite),
        .data_in(WriteData),
        .addr(Adr[11:2]),
        .data_out(ReadData)
    );

    register memory_register(
        .clk(clk), 
        .reset(reset), 
        .enable(1),
        .in(ReadData),
        .out(Data)
    );


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
    four_one_mux srcb_mux(
        .mx(AlUSrcA),
        .a(PCout),
        .b(OldPC),
        .c(A),
        .d(0),
        .out(SrcA)
    );

    // Src B Mux
    logic [31:0] SrcB;
    four_one_mux srcb_mux(
        .mx(ALUSrcB),
        .a(WriteData),
        .b(ImmExt),
        .c(4),
        .d(0),
        .out(SrcB)
    );

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

    four_one_mux result_mux (
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

    FSM fsm_instance (
        .op(Instr[6:0]),
        .funct7_5(Instr[30]),
        .funct3(Instr[14:12]),
        .reset(reset).
        .PCWrite(PCwrite),
        .AdrSrc(AdrSrc),
        .MemWrite(MemWrite),
        .IRWrite(IRWrite),
        .ResultSrc(ResultSrc),
        .ALUControl(ALUControl),
        .ALUSrcB(ALUSrcB),
        .AlUSrcA(AlUSrcA),
        .ImmSrc(ImmSrc),
        .RegWrite(RegWrite)
    );

    // Extend 
    logic [31:0] ImmExt;
    Extend extend_instance (
        .ImmSrc(ImmSrc),
        .instr(instr[31:7]),
        .ImmExt(ImmExt)
    );

endmodule