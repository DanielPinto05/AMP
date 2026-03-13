import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from cocotb.types import LogicArray
import logging
import random


MASK32 = 0xFFFFFFFF

# based on the package values you showed earlier
OP_ADD = 0b0000
OP_SUB = 0b0001

# from your mux ordering in amp
SRCA_A = 2          # .c(A)
SRCB_WRITEDATA = 0  # .a(WriteData)
RESULTSRC_ALURESULT = 2  # .c(ALUResult)

# change this if your register array inside register_file is named differently
RF_ARRAY_NAME = "GEN_REGS"


def u32(x: int) -> int:
    return x & MASK32


def encode_rtype(funct7: int, rs2: int, rs1: int, funct3: int, rd: int, opcode: int = 0x33) -> int:
    return (
        ((funct7 & 0x7F) << 25)
        | ((rs2 & 0x1F) << 20)
        | ((rs1 & 0x1F) << 15)
        | ((funct3 & 0x7) << 12)
        | ((rd & 0x1F) << 7)
        | (opcode & 0x7F)
    )


def add_instr(rd: int, rs1: int, rs2: int) -> int:
    return encode_rtype(funct7=0x00, rs2=rs2, rs1=rs1, funct3=0x0, rd=rd)


def sub_instr(rd: int, rs1: int, rs2: int) -> int:
    return encode_rtype(funct7=0x20, rs2=rs2, rs1=rs1, funct3=0x0, rd=rd)


def rf_array(dut):
    try:
        return getattr(dut.u_register_file, RF_ARRAY_NAME)
    except AttributeError as e:
        raise RuntimeError(
            f"Could not find register array dut.u_register_file.{RF_ARRAY_NAME}. "
            f"Rename RF_ARRAY_NAME in the test to match your register file internals."
        ) from e


def clear_regfile(dut):
    regs = rf_array(dut)
    for i in range(32):
        regs[i].value = 0


def write_reg(dut, idx: int, val: int):
    # x0 must remain zero
    if idx == 0:
        return
    rf_array(dut)[idx].value = u32(val)


def read_reg(dut, idx: int) -> int:
    if idx == 0:
        return 0
    return int(rf_array(dut)[idx].value) & MASK32


async def settle():
    await Timer(1, unit="ns")


async def reset_dut(dut):
    dut.reset.value = 1
    dut.pc_input.value = 0

    # if you bypassed the FSM for this test, initialize the control lines here
    dut.PCwrite.value = 0
    dut.AdrSrc.value = 0
    dut.MemWrite.value = 0
    dut.IRWrite.value = 0
    dut.ResultSrc.value = RESULTSRC_ALURESULT
    dut.ALUControl.value = OP_ADD
    dut.ALUSrcB.value = SRCB_WRITEDATA
    dut.AlUSrcA.value = SRCA_A
    dut.RegWrite.value = 0

    clear_regfile(dut)

    await RisingEdge(dut.clk)
    await settle()
    await RisingEdge(dut.clk)
    await settle()

    dut.reset.value = 0
    await RisingEdge(dut.clk)
    await settle()


async def run_rtype_op(dut, *, op_name: str, rs1: int, rs2: int, rd: int, rs1_seed: int, rs2_seed: int):
    clear_regfile(dut)

    write_reg(dut, rs1, rs1_seed)
    write_reg(dut, rs2, rs2_seed)

    src1 = read_reg(dut, rs1)
    src2 = read_reg(dut, rs2)

    if op_name == "add":
        instr = add_instr(rd=rd, rs1=rs1, rs2=rs2)
        exp = u32(src1 + src2)
        dut.ALUControl.value = OP_ADD
    elif op_name == "sub":
        instr = sub_instr(rd=rd, rs1=rs1, rs2=rs2)
        exp = u32(src1 - src2)
        dut.ALUControl.value = OP_SUB
    else:
        raise ValueError(f"Unsupported op_name {op_name}")

    dut.Instr.value = instr
    dut.AlUSrcA.value = SRCA_A
    dut.ALUSrcB.value = SRCB_WRITEDATA
    dut.ResultSrc.value = RESULTSRC_ALURESULT

    # first cycle: latch rd1 -> A and rd2 -> WriteData
    dut.RegWrite.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # second cycle: write result back to rd
    dut.RegWrite.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    dut.RegWrite.value = 0

    got_rd = read_reg(dut, rd)
    exp_rd = 0 if rd == 0 else exp

    assert got_rd == exp_rd, (
        f"[{op_name}] rs1=x{rs1} rs2=x{rs2} rd=x{rd} "
        f"src1=0x{src1:08X} src2=0x{src2:08X} "
        f"expected rd=0x{exp_rd:08X}, got rd=0x{got_rd:08X}"
    )

    assert read_reg(dut, 0) == 0, f"x0 changed unexpectedly"


@cocotb.test()
async def amp_add_sub_test(dut):
    """Directed + randomized ADD/SUB datapath test for amp."""
    logger = logging.getLogger("AMP_add_sub_test")
    logger.setLevel(logging.INFO)
    logger.info("Starting AMP_add_sub_test")

    file_handler = logging.FileHandler("AMP_add_sub_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:
        logger.addHandler(file_handler)

    random.seed(12345)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # directed tests
    directed = [
        # op, rs1, rs2, rd, rs1_seed, rs2_seed
        ("add", 1, 2, 3, 5, 7),                     # normal add
        ("sub", 8, 9, 10, 20, 4),                   # normal sub
        ("add", 0, 5, 6, 0, 0x12345678),            # x0 as rs1
        ("add", 5, 0, 7, 0xCAFEBABE, 0),            # x0 as rs2
        ("sub", 0, 7, 8, 0, 3),                     # 0 - 3
        ("add", 4, 4, 11, 0x10, 0x99),              # same source register index; last seed wins
        ("sub", 12, 13, 0, 99, 11),                 # write into x0; must stay zero
        ("add", 31, 30, 29, 0xFFFFFFFF, 1),         # overflow wrap
        ("sub", 15, 16, 17, 0, 1),                  # underflow wrap
    ]

    for i, (op, rs1, rs2, rd, a, b) in enumerate(directed):
        logger.info(
            f"[directed {i}] op={op} rs1=x{rs1} rs2=x{rs2} rd=x{rd} "
            f"seed1=0x{u32(a):08X} seed2=0x{u32(b):08X}"
        )
        await run_rtype_op(
            dut,
            op_name=op,
            rs1=rs1,
            rs2=rs2,
            rd=rd,
            rs1_seed=a,
            rs2_seed=b,
        )

    # randomized tests
    for i in range(300):
        op = random.choice(["add", "sub"])
        rs1 = random.randint(0, 31)
        rs2 = random.randint(0, 31)
        rd = random.randint(0, 31)
        a = random.getrandbits(32)
        b = random.getrandbits(32)

        logger.info(
            f"[rand {i}] op={op} rs1=x{rs1} rs2=x{rs2} rd=x{rd} "
            f"seed1=0x{a:08X} seed2=0x{b:08X}"
        )

        await run_rtype_op(
            dut,
            op_name=op,
            rs1=rs1,
            rs2=rs2,
            rd=rd,
            rs1_seed=a,
            rs2_seed=b,
        )

    logger.info("All AMP add/sub tests passed!")