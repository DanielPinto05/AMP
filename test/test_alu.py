import cocotb
from cocotb.triggers import Timer
import logging
import random


MASK32 = 0xFFFFFFFF

# Must match alu_defs package
OP_ADD  = 0b0000
OP_SUB  = 0b0001
OP_SLL  = 0b0010
OP_SRA  = 0b0011
OP_SRL  = 0b0100
OP_OR   = 0b0101
OP_XOR  = 0b0110
OP_SSLT = 0b0111
OP_USLT = 0b1000
OP_AND  = 0b1001


def u32(x: int) -> int:
    return x & MASK32


def s32(x: int) -> int:
    x &= MASK32
    return x if x < 0x80000000 else x - 0x100000000


def model_alu(a: int, b: int, ctrl: int) -> int:
    a_u = u32(a)
    b_u = u32(b)
    shamt = b_u & 0x1F

    if ctrl == OP_ADD:
        return u32(a_u + b_u)

    elif ctrl == OP_SUB:
        return u32(a_u - b_u)

    elif ctrl == OP_SLL:
        return u32(a_u << shamt)

    elif ctrl == OP_SRA:
        return u32(s32(a_u) >> shamt)

    elif ctrl == OP_SRL:
        return u32(a_u >> shamt)

    elif ctrl == OP_OR:
        return u32(a_u | b_u)

    elif ctrl == OP_XOR:
        return u32(a_u ^ b_u)

    elif ctrl == OP_SSLT:
        return 1 if s32(a_u) < s32(b_u) else 0

    elif ctrl == OP_USLT:
        return 1 if a_u < b_u else 0

    elif ctrl == OP_AND:
        return u32(a_u & b_u)

    else:
        return 0


@cocotb.test()
async def alu_test(dut):
    """Directed + randomized tests for alu.sv"""
    logger = logging.getLogger("alu_test")
    logger.setLevel(logging.INFO)
    logger.info("Starting alu_test")

    file_handler = logging.FileHandler("alu_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:
        logger.addHandler(file_handler)

    async def settle():
        await Timer(1, unit="ns")

    # Directed tests
    vectors = [
        # ADD
        (OP_ADD, 0x00000000, 0x00000000, "ADD zero"),
        (OP_ADD, 0x00000001, 0x00000002, "ADD small"),
        (OP_ADD, 0xFFFFFFFF, 0x00000001, "ADD wrap"),

        # SUB
        (OP_SUB, 0x00000005, 0x00000003, "SUB small"),
        (OP_SUB, 0x00000000, 0x00000001, "SUB wrap"),
        (OP_SUB, 0x80000000, 0x00000001, "SUB negative boundary"),

        # SLL
        (OP_SLL, 0x00000001, 0x00000001, "SLL by 1"),
        (OP_SLL, 0x00000001, 0x0000001F, "SLL by 31"),
        (OP_SLL, 0x00000001, 0x00000020, "SLL by 32 -> 0 shift"),
        (OP_SLL, 0x12345678, 0x00000004, "SLL random"),

        # SRA
        (OP_SRA, 0x80000000, 0x00000001, "SRA sign extend"),
        (OP_SRA, 0xFFFFFFFF, 0x00000004, "SRA -1 stays -1"),
        (OP_SRA, 0x7FFFFFFF, 0x00000001, "SRA positive"),
        (OP_SRA, 0x80000000, 0x00000020, "SRA by 32 -> 0 shift"),

        # SRL
        (OP_SRL, 0x80000000, 0x00000001, "SRL logical"),
        (OP_SRL, 0xFFFFFFFF, 0x00000004, "SRL all ones"),
        (OP_SRL, 0x12345678, 0x00000008, "SRL random"),
        (OP_SRL, 0x80000000, 0x00000020, "SRL by 32 -> 0 shift"),

        # OR
        (OP_OR, 0xAAAAAAAA, 0x55555555, "OR complement"),
        (OP_OR, 0x12340000, 0x00005678, "OR random"),

        # XOR
        (OP_XOR, 0xAAAAAAAA, 0x55555555, "XOR complement"),
        (OP_XOR, 0xDEADBEEF, 0xDEADBEEF, "XOR same -> 0"),

        # Signed SLT
        (OP_SSLT, 0xFFFFFFFF, 0x00000001, "SLT signed -1 < 1"),
        (OP_SSLT, 0x00000001, 0xFFFFFFFF, "SLT signed 1 !< -1"),
        (OP_SSLT, 0x80000000, 0x00000000, "SLT signed min < 0"),
        (OP_SSLT, 0x7FFFFFFF, 0x80000000, "SLT signed max !< min"),

        # Unsigned SLT
        (OP_USLT, 0x00000001, 0xFFFFFFFF, "SLT unsigned 1 < max"),
        (OP_USLT, 0xFFFFFFFF, 0x00000001, "SLT unsigned max !< 1"),
        (OP_USLT, 0x80000000, 0x7FFFFFFF, "SLT unsigned compare"),

        # AND
        (OP_AND, 0xAAAAAAAA, 0x55555555, "AND complement"),
        (OP_AND, 0xDEADBEEF, 0x0F0F0F0F, "AND mask"),

        # default
        (0b1010, 0x12345678, 0x9ABCDEF0, "DEFAULT 10"),
        (0b1111, 0xFFFFFFFF, 0xFFFFFFFF, "DEFAULT 15"),
    ]

    for i, (ctrl, a, b, name) in enumerate(vectors):
        dut.ALUctrl.value = ctrl
        dut.a.value = a
        dut.b.value = b
        await settle()

        got = int(dut.ALUout.value)
        exp = model_alu(a, b, ctrl)

        assert got == exp, (
            f"[directed {i}] {name} "
            f"ctrl={ctrl:04b} a=0x{u32(a):08X} b=0x{u32(b):08X} "
            f"expected=0x{exp:08X}, got=0x{got:08X}"
        )

    # Randomized valid-op tests
    valid_ops = [
        OP_ADD, OP_SUB, OP_SLL, OP_SRA, OP_SRL,
        OP_OR, OP_XOR, OP_SSLT, OP_USLT, OP_AND
    ]

    for i in range(500):
        ctrl = random.choice(valid_ops)
        a = random.getrandbits(32)
        b = random.getrandbits(32)

        dut.ALUctrl.value = ctrl
        dut.a.value = a
        dut.b.value = b
        await settle()

        got = int(dut.ALUout.value)
        exp = model_alu(a, b, ctrl)

        assert got == exp, (
            f"[rand {i}] ctrl={ctrl:04b} a=0x{a:08X} b=0x{b:08X} "
            f"expected=0x{exp:08X}, got=0x{got:08X}"
        )

    # Randomized default-case tests
    invalid_ops = [0b1010, 0b1011, 0b1100, 0b1101, 0b1110, 0b1111]

    for i in range(50):
        ctrl = random.choice(invalid_ops)
        a = random.getrandbits(32)
        b = random.getrandbits(32)

        dut.ALUctrl.value = ctrl
        dut.a.value = a
        dut.b.value = b
        await settle()

        got = int(dut.ALUout.value)
        assert got == 0, (
            f"[default rand {i}] ctrl={ctrl:04b} a=0x{a:08X} b=0x{b:08X} "
            f"expected=0x00000000, got=0x{got:08X}"
        )

    logger.info("All ALU tests passed!")