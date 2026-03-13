import cocotb
from cocotb.triggers import Timer
import logging
import random


MASK32 = 0xFFFFFFFF

I = 0b000
S = 0b001
B = 0b010
U = 0b011
J = 0b100


def u32(x: int) -> int:
    return x & MASK32


def sign_extend(val: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return u32((val & (sign_bit - 1)) - (val & sign_bit))


def instr31_7(full_instr: int) -> int:
    """Return bits [31:7] as the DUT expects."""
    return (full_instr >> 7) & ((1 << 25) - 1)


def model_extend(full_instr: int, imm_src: int) -> int:
    """Golden model using full 32-bit instruction bit positions."""
    bit31 = (full_instr >> 31) & 1

    if imm_src == I:
        imm12 = (full_instr >> 20) & 0xFFF
        return sign_extend(imm12, 12)

    elif imm_src == S:
        imm12 = (((full_instr >> 25) & 0x7F) << 5) | ((full_instr >> 7) & 0x1F)
        return sign_extend(imm12, 12)

    elif imm_src == B:
        imm13 = (
            (bit31 << 12)
            | (((full_instr >> 7) & 1) << 11)
            | (((full_instr >> 25) & 0x3F) << 5)
            | (((full_instr >> 8) & 0xF) << 1)
        )
        return sign_extend(imm13, 13)

    elif imm_src == U:
        return u32(full_instr & 0xFFFFF000)

    elif imm_src == J:
        imm21 = (
            (bit31 << 20)
            | (((full_instr >> 12) & 0xFF) << 12)
            | (((full_instr >> 20) & 1) << 11)
            | (((full_instr >> 21) & 0x3FF) << 1)
        )
        return sign_extend(imm21, 21)

    else:
        return 0


# -------------------------
# Small encoders for tests
# -------------------------

def make_i_instr(imm12: int) -> int:
    imm12 &= 0xFFF
    return imm12 << 20


def make_s_instr(imm12: int) -> int:
    imm12 &= 0xFFF
    upper = (imm12 >> 5) & 0x7F
    lower = imm12 & 0x1F
    return (upper << 25) | (lower << 7)


def make_b_instr(imm13: int) -> int:
    # B immediate must be even since bit 0 is always 0
    imm13 &= 0x1FFF
    b12 = (imm13 >> 12) & 1
    b11 = (imm13 >> 11) & 1
    b10_5 = (imm13 >> 5) & 0x3F
    b4_1 = (imm13 >> 1) & 0xF
    return (
        (b12 << 31)
        | (b11 << 7)
        | (b10_5 << 25)
        | (b4_1 << 8)
    )


def make_u_instr(imm20: int) -> int:
    imm20 &= 0xFFFFF
    return imm20 << 12


def make_j_instr(imm21: int) -> int:
    # J immediate must be even since bit 0 is always 0
    imm21 &= 0x1FFFFF
    j20 = (imm21 >> 20) & 1
    j19_12 = (imm21 >> 12) & 0xFF
    j11 = (imm21 >> 11) & 1
    j10_1 = (imm21 >> 1) & 0x3FF
    return (
        (j20 << 31)
        | (j19_12 << 12)
        | (j11 << 20)
        | (j10_1 << 21)
    )


@cocotb.test()
async def extend_test(dut):
    """Directed + randomized tests for extend.sv"""
    logger = logging.getLogger("extend_test")
    logger.setLevel(logging.INFO)
    logger.info("Starting extend_test")

    file_handler = logging.FileHandler("extend_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:
        logger.addHandler(file_handler)

    async def settle():
        await Timer(1, unit="ns")

    # -------------------------
    # Directed tests
    # -------------------------
    directed = [
        # I-type
        (I, make_i_instr(0x000), "I zero"),
        (I, make_i_instr(0x001), "I +1"),
        (I, make_i_instr(0x7FF), "I max positive"),
        (I, make_i_instr(0x800), "I most negative"),
        (I, make_i_instr(0xFFF), "I -1"),

        # S-type
        (S, make_s_instr(0x000), "S zero"),
        (S, make_s_instr(0x001), "S +1"),
        (S, make_s_instr(0x7FF), "S max positive"),
        (S, make_s_instr(0x800), "S most negative"),
        (S, make_s_instr(0xFFF), "S -1"),

        # B-type
        (B, make_b_instr(0x0000), "B zero"),
        (B, make_b_instr(0x0002), "B +2"),
        (B, make_b_instr(0x0FFE), "B max positive"),
        (B, make_b_instr(0x1000), "B most negative"),
        (B, make_b_instr(0x1FFE), "B -2"),

        # U-type
        (U, make_u_instr(0x00000), "U zero"),
        (U, make_u_instr(0x00001), "U low"),
        (U, make_u_instr(0xABCDE), "U random"),
        (U, make_u_instr(0xFFFFF), "U all ones"),

        # J-type
        (J, make_j_instr(0x00000), "J zero"),
        (J, make_j_instr(0x00002), "J +2"),
        (J, make_j_instr(0x0FFFFE), "J max positive-ish"),
        (J, make_j_instr(0x100000), "J most negative"),
        (J, make_j_instr(0x1FFFFE), "J -2"),

        # default cases
        (0b101, 0xFFFFFFFF, "default 101"),
        (0b110, 0x12345678, "default 110"),
        (0b111, 0x89ABCDEF, "default 111"),
    ]

    for i, (imm_src, full_instr, name) in enumerate(directed):
        dut.ImmSrc.value = imm_src
        dut.instr.value = instr31_7(full_instr)
        await settle()

        got = int(dut.ImmExt.value)
        exp = model_extend(full_instr, imm_src)

        assert got == exp, (
            f"[directed {i}] {name} "
            f"ImmSrc={imm_src:03b} full_instr=0x{full_instr:08X} "
            f"expected=0x{exp:08X}, got=0x{got:08X}"
        )

    # -------------------------
    # Randomized tests
    # -------------------------
    for i in range(200):
        imm_src = random.choice([I, S, B, U, J])

        if imm_src == I:
            imm12 = random.getrandbits(12)
            full_instr = make_i_instr(imm12)

        elif imm_src == S:
            imm12 = random.getrandbits(12)
            full_instr = make_s_instr(imm12)

        elif imm_src == B:
            imm13 = random.getrandbits(13) & 0x1FFE  # force bit0 = 0
            full_instr = make_b_instr(imm13)

        elif imm_src == U:
            imm20 = random.getrandbits(20)
            full_instr = make_u_instr(imm20)

        else:  # J
            imm21 = random.getrandbits(21) & 0x1FFFFE  # force bit0 = 0
            full_instr = make_j_instr(imm21)

        dut.ImmSrc.value = imm_src
        dut.instr.value = instr31_7(full_instr)
        await settle()

        got = int(dut.ImmExt.value)
        exp = model_extend(full_instr, imm_src)

        assert got == exp, (
            f"[rand {i}] ImmSrc={imm_src:03b} full_instr=0x{full_instr:08X} "
            f"expected=0x{exp:08X}, got=0x{got:08X}"
        )

    # -------------------------
    # Randomized default-case tests
    # -------------------------
    for i in range(30):
        imm_src = random.choice([0b101, 0b110, 0b111])
        full_instr = random.getrandbits(32)

        dut.ImmSrc.value = imm_src
        dut.instr.value = instr31_7(full_instr)
        await settle()

        got = int(dut.ImmExt.value)
        assert got == 0, (
            f"[default rand {i}] ImmSrc={imm_src:03b} full_instr=0x{full_instr:08X} "
            f"expected=0x00000000, got=0x{got:08X}"
        )

    logger.info("All extend tests passed!")