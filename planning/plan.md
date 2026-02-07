# AMP - Multicycle RISC-V Processor Implementation Plan

## Architecture Overview
Implementing the multicycle processor architecture from Harris & Harris. This processor executes instructions over multiple clock cycles with shared functional units.

## Current Status

### ✅ Completed Modules
- **ALU.sv** - Full ALU with 10 operations (ADD, SUB, SLL, SRA, SRL, OR, XOR, SLT, SLTU, AND)
- **Extend.sv** - Immediate extension for all 5 types (I, S, B, U, J)
- **register.sv** - 32-register file with dual read ports and write enable
- **ram.sv** - 1K x 32-bit memory with synchronous read/write

### 🚧 In Progress / Incomplete
- **amp.sv** - Top-level module skeleton exists but needs full datapath implementation
- **FSM.sv** - Empty/minimal, needs complete control unit implementation

---

## Implementation Plan

## Phase 1: Control Unit (FSM.sv)

### FSM.sv - Main Control FSM
**Purpose:** Generate all control signals based on instruction opcode and current state

**States Needed:**
1. **FETCH** - Fetch instruction from memory
2. **DECODE** - Decode instruction and read registers
3. **MEMADR** - Calculate memory address (for lw/sw)
4. **MEMREAD** - Read from memory (for lw)
5. **MEMWRITE** - Write to memory (for sw)
6. **MEMWB** - Write memory data back to register
7. **EXECUTER** - Execute R-type ALU operation
8. **EXECUTEI** - Execute I-type ALU operation
9. **ALUWB** - Write ALU result back to register
10. **BRANCH** - Evaluate branch and update PC
11. **JAL** - Jump and link
12. **LUI** - Load upper immediate

**Inputs:**
- `clk` - System clock
- `reset` - Synchronous reset
- `op[6:0]` - Opcode from instruction register
- `funct3[2:0]` - Function code for instruction variants
- `funct7[6]` - Additional function bit for R-type
- `Zero` - Zero flag from ALU

**Outputs:**
- `PCWrite` - Enable PC update
- `AdrSrc` - Select address source (PC or ALU result) for memory
- `MemWrite` - Memory write enable
- `IRWrite` - Instruction register write enable
- `ResultSrc[1:0]` - Select result to write back (ALU, Memory, PC+4)
- `ALUControl[3:0]` - ALU operation select
- `ALUSrcA[1:0]` - Select first ALU operand (PC, Old PC, reg A)
- `ALUSrcB[1:0]` - Select second ALU operand (reg B, immediate, 4)
- `ImmSrc[2:0]` - Immediate extension type
- `RegWrite` - Register file write enable
- `PCUpdate` - Conditional PC update for branches

**FSM State Transitions:**
```
FETCH → DECODE (always)
DECODE →
    - MEMADR (lw/sw)
    - EXECUTER (R-type)
    - EXECUTEI (I-type ALU)
    - BRANCH (beq, bne, etc.)
    - JAL (jal)
    - LUI (lui)
MEMADR → MEMREAD (lw) or MEMWRITE (sw)
MEMREAD → MEMWB
MEMWB → FETCH
MEMWRITE → FETCH
EXECUTER → ALUWB
EXECUTEI → ALUWB
ALUWB → FETCH
BRANCH → FETCH
JAL → ALUWB
LUI → ALUWB
```

---

## Phase 2: Datapath Components

### Create New Modules:

#### mux2.sv - 2-to-1 Multiplexer
**Purpose:** Select between two inputs
```systemverilog
module mux2 #(parameter WIDTH = 32)(
    input logic [WIDTH-1:0] d0,
    input logic [WIDTH-1:0] d1,
    input logic sel,
    output logic [WIDTH-1:0] y
);
```

#### mux3.sv - 3-to-1 Multiplexer
**Purpose:** Select between three inputs
```systemverilog
module mux3 #(parameter WIDTH = 32)(
    input logic [WIDTH-1:0] d0,
    input logic [WIDTH-1:0] d1,
    input logic [WIDTH-1:0] d2,
    input logic [1:0] sel,
    output logic [WIDTH-1:0] y
);
```

#### mux4.sv - 4-to-1 Multiplexer
**Purpose:** Select between four inputs (may be needed for complex datapaths)

#### adder.sv - Simple Adder
**Purpose:** PC + 4 incrementer (or use ALU)
```systemverilog
module adder(
    input logic [31:0] a,
    input logic [31:0] b,
    output logic [31:0] sum
);
```

---

## Phase 3: Top-Level Integration (amp.sv)

### Complete amp.sv Module

**External Interface:**
- `clk` - System clock
- `reset` - Asynchronous or synchronous reset
- `[31:0] MemData` - Data from external memory (if unified)

**Internal Signals:**
```systemverilog
// Datapath control signals (from FSM)
logic PCWrite, AdrSrc, MemWrite, IRWrite;
logic [1:0] ResultSrc, ALUSrcA, ALUSrcB;
logic [2:0] ImmSrc;
logic [3:0] ALUControl;
logic RegWrite;

// Datapath signals
logic [31:0] PC, PCNext, PCPlus4;
logic [31:0] Instr, Data;
logic [31:0] A, B;        // Register outputs (stored in A and B registers)
logic [31:0] ImmExt;
logic [31:0] SrcA, SrcB;
logic [31:0] ALUResult, ALUOut;
logic [31:0] Result;
logic [31:0] RD1, RD2, WD3;
logic [31:0] Adr;
logic Zero;
```

**Datapath Registers Needed:**
- PC register (program counter)
- Instruction register (IR)
- Data register (stores memory read data)
- A register (stores rs1 data)
- B register (stores rs2 data)
- ALUOut register (stores ALU result)

**Component Instantiations:**
1. Program Counter Register
2. Instruction Memory (RAM instance)
3. Instruction Register
4. Register File
5. Immediate Extender
6. A and B Registers (for register data)
7. ALU
8. ALUOut Register
9. Data Memory (RAM instance)
10. Data Register
11. FSM (Control Unit)
12. Multiplexers for:
    - ALU source A (mux3: PC, Old PC, reg A)
    - ALU source B (mux3: reg B, immediate, 4)
    - Result source (mux3: ALU, memory data, PC+4)
    - Memory address (mux2: PC or ALU result)

---

## Phase 4: Instruction Implementation

### RV32I Instructions to Implement

#### R-Type (Register-Register)
- **add** rd, rs1, rs2 - Add
- **sub** rd, rs1, rs2 - Subtract
- **sll** rd, rs1, rs2 - Shift left logical
- **slt** rd, rs1, rs2 - Set less than (signed)
- **sltu** rd, rs1, rs2 - Set less than (unsigned)
- **xor** rd, rs1, rs2 - XOR
- **srl** rd, rs1, rs2 - Shift right logical
- **sra** rd, rs1, rs2 - Shift right arithmetic
- **or** rd, rs1, rs2 - OR
- **and** rd, rs1, rs2 - AND

**Opcode:** 0110011

#### I-Type (Immediate)
- **addi** rd, rs1, imm - Add immediate
- **xori** rd, rs1, imm - XOR immediate
- **ori** rd, rs1, imm - OR immediate
- **andi** rd, rs1, imm - AND immediate
- **slli** rd, rs1, shamt - Shift left logical immediate
- **srli** rd, rs1, shamt - Shift right logical immediate
- **srai** rd, rs1, shamt - Shift right arithmetic immediate
- **slti** rd, rs1, imm - Set less than immediate (signed)
- **sltiu** rd, rs1, imm - Set less than immediate (unsigned)

**Opcode:** 0010011

#### Load/Store
- **lw** rd, offset(rs1) - Load word
- **sw** rs2, offset(rs1) - Store word

**Opcodes:** lw=0000011, sw=0100011

#### Branch
- **beq** rs1, rs2, offset - Branch if equal
- **bne** rs1, rs2, offset - Branch if not equal
- **blt** rs1, rs2, offset - Branch if less than (signed)
- **bge** rs1, rs2, offset - Branch if greater/equal (signed)
- **bltu** rs1, rs2, offset - Branch if less than (unsigned)
- **bgeu** rs1, rs2, offset - Branch if greater/equal (unsigned)

**Opcode:** 1100011

#### Jump
- **jal** rd, offset - Jump and link
- **jalr** rd, offset(rs1) - Jump and link register

**Opcodes:** jal=1101111, jalr=1100111

#### Upper Immediate
- **lui** rd, imm - Load upper immediate
- **auipc** rd, imm - Add upper immediate to PC

**Opcodes:** lui=0110111, auipc=0010111

---

## Phase 5: ALU Control Decoder

### ALUDecoder Module (can be part of FSM.sv or separate)

**Purpose:** Decode instruction to generate ALUControl[3:0]

**Inputs:**
- `opcode[6:0]`
- `funct3[2:0]`
- `funct7[6]` (bit 30 for sub/sra)

**Output:**
- `ALUControl[3:0]` mapped to ALU operations:
  - 0: ADD
  - 1: SUB
  - 2: SLL
  - 3: SRA
  - 4: SRL
  - 5: OR
  - 6: XOR
  - 7: SLT
  - 8: SLTU
  - 9: AND

---

## Phase 6: Testing Strategy

### Unit Tests (cocotb)
1. **test_FSM.py** - Test FSM state transitions and control signals
2. **test_alu.py** - Verify all ALU operations (if not done)
3. **test_extend.py** - Verify all immediate types (if not done)
4. **test_register_file.py** - Test reads/writes, x0 hardwired to 0
5. **test_datapath.py** - Test datapath with manual control signals

### Integration Tests
6. **test_instructions.py** - Test each RV32I instruction individually
   - R-type: add, sub, sll, slt, sltu, xor, srl, sra, or, and
   - I-type: addi, xori, ori, andi, slli, srli, srai, slti, sltiu
   - Load/Store: lw, sw
   - Branch: beq, bne, blt, bge, bltu, bgeu
   - Jump: jal, jalr
   - Upper: lui, auipc

### Full System Tests
7. **test_programs.py** - Run complete RISC-V programs
   - Fibonacci sequence
   - Factorial calculation
   - Array sum
   - Bubble sort
   - Memory read/write patterns

---

## Phase 7: Verification & Debug

### Checklist
- [ ] All FSM states reachable
- [ ] All control signals generated correctly
- [ ] PC updates correctly (sequential, branch, jump)
- [ ] Register file reads/writes working
- [ ] Memory loads/stores functioning
- [ ] Immediate extension correct for all types
- [ ] ALU operations verified
- [ ] Branch conditions evaluated properly
- [ ] No combinational loops in datapath
- [ ] Reset initializes all registers
- [ ] Timing meets requirements

### Debugging Tools
- Waveform viewer (GTKWave)
- cocotb logging
- Assertions in testbenches
- Instruction trace (PC, instruction, register writes)

---

## File Structure Summary

```
AMP/
├── src/
│   ├── amp.sv                 [NEEDS COMPLETION - Top-level datapath]
│   ├── FSM.sv                 [NEEDS IMPLEMENTATION - Control FSM]
│   ├── ALU.sv                 [COMPLETE]
│   ├── Extend.sv              [COMPLETE]
│   ├── register.sv            [COMPLETE]
│   ├── ram.sv                 [COMPLETE]
│   ├── mux2.sv                [NEEDS CREATION]
│   ├── mux3.sv                [NEEDS CREATION]
│   └── adder.sv               [OPTIONAL - can use ALU]
├── test/
│   ├── test_FSM.py            [NEEDS CREATION]
│   ├── test_datapath.py       [NEEDS CREATION]
│   ├── test_instructions.py   [NEEDS CREATION]
│   ├── test_programs.py       [NEEDS CREATION]
│   └── Makefile               [UPDATE as needed]
├── planning/
│   └── plan.md                [THIS FILE]
└── README.md
```

---

## Implementation Order

1. **Multiplexers** (mux2.sv, mux3.sv) - Simple, reusable
2. **FSM.sv** - Control unit with all states and signals
3. **amp.sv completion** - Wire up entire datapath
4. **Unit tests** - Verify each component
5. **Instruction tests** - Test each instruction type
6. **Integration tests** - Run full programs
7. **Optimization** - Timing, area (future)

---

## Notes & Design Decisions

### Multicycle Advantages
- Shared functional units (one ALU, one memory)
- Lower hardware cost
- Variable cycle count per instruction

### Key Design Choices
- **Memory:** Separate instruction and data memory (Harvard architecture) vs unified
  - Current: Appears to be Harvard (IMEM and DMEM in amp.sv)
- **PC Update:** Combinational vs registered
  - Recommended: Registered with enable (PCWrite)
- **Reset:** Synchronous vs asynchronous
  - Current: Synchronous in existing modules
- **ALU for PC increment:** Can use ALU or dedicated adder
  - Recommended: Use ALU to save area

### Potential Issues to Watch
1. Memory addressing: Byte addressing vs word addressing
2. Sign extension in branches and comparisons
3. PC alignment (PC must be multiple of 4)
4. Register x0 must always read as 0
5. Write-after-read hazards in same cycle (shouldn't occur in multicycle)

---

## Success Criteria

### Minimum Viable Processor
- Execute all RV32I base instructions
- Pass directed tests for each instruction
- Run simple program (e.g., calculate sum of array)

### Full Success
- All 40+ RV32I instructions working
- Pass riscv-tests compliance suite
- Run complex programs (sorting, recursion)
- Clean waveforms with no X's or Z's
- Documented and maintainable code

---

## Resources
- Harris & Harris "Digital Design and Computer Architecture" - Chapter 7
- RISC-V Specification: https://riscv.org/technical/specifications/
- RISC-V Instruction Set Manual
- cocotb documentation: https://docs.cocotb.org/
