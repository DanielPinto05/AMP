import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import logging
import random


MASK32 = 0xFFFFFFFF


def u32(x: int) -> int:
    return x & MASK32


@cocotb.test()
async def register_file_test(dut):
    """Directed + randomized tests for register_file.sv"""
    logger = logging.getLogger("register_file_test")
    logger.setLevel(logging.INFO)
    logger.info("Starting register_file_test")

    file_handler = logging.FileHandler("register_file_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:
        logger.addHandler(file_handler)

    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    async def settle():
        await Timer(1, unit="ns")

    async def apply_reset():
        dut.reset.value = 1
        dut.RegWrite.value = 0
        dut.rs1.value = 0
        dut.rs2.value = 0
        dut.rd.value = 0
        dut.wd.value = 0
        await settle()
        await RisingEdge(dut.clk)
        await settle()
        await RisingEdge(dut.clk)
        await settle()
        dut.reset.value = 0
        await settle()

    async def write_reg(rd: int, data: int):
        dut.rd.value = rd
        dut.wd.value = u32(data)
        dut.RegWrite.value = 1
        await settle()
        await RisingEdge(dut.clk)
        await settle()
        dut.RegWrite.value = 0
        await settle()

    async def read_regs(rs1: int, rs2: int):
        dut.rs1.value = rs1
        dut.rs2.value = rs2
        await settle()
        return int(dut.rd1.value), int(dut.rd2.value)

    async def check_read(rs1: int, rs2: int, exp1: int, exp2: int, tag: str):
        got1, got2 = await read_regs(rs1, rs2)
        assert got1 == u32(exp1), (
            f"[{tag}] rs1=x{rs1} expected rd1=0x{u32(exp1):08X}, got=0x{got1:08X}"
        )
        assert got2 == u32(exp2), (
            f"[{tag}] rs2=x{rs2} expected rd2=0x{u32(exp2):08X}, got=0x{got2:08X}"
        )

    # golden model
    model = [0] * 32

    # -------------------------
    # Reset test
    # -------------------------
    await apply_reset()

    for i in range(0, 32, 2):
        exp1 = 0
        exp2 = 0
        await check_read(i, min(i + 1, 31), exp1, exp2, f"reset check {i//2}")

    # -------------------------
    # Directed tests
    # -------------------------

    # 1) Basic write/read
    await write_reg(1, 0x12345678)
    model[1] = 0x12345678
    await check_read(1, 0, model[1], 0, "directed basic write/read")

    # 2) Another write/read
    await write_reg(2, 0xDEADBEEF)
    model[2] = 0xDEADBEEF
    await check_read(1, 2, model[1], model[2], "directed second write")

    # 3) Write high register
    await write_reg(31, 0xCAFEBABE)
    model[31] = 0xCAFEBABE
    await check_read(31, 2, model[31], model[2], "directed high register")

    # 4) Overwrite same register
    await write_reg(2, 0x0BADF00D)
    model[2] = 0x0BADF00D
    await check_read(2, 31, model[2], model[31], "directed overwrite")

    # 5) x0 must always read as zero
    await write_reg(0, 0xFFFFFFFF)
    model[0] = 0
    await check_read(0, 0, 0, 0, "directed x0 hardwired zero")
    await check_read(0, 2, 0, model[2], "directed x0 with another register")

    # 6) RegWrite = 0 should not change anything
    dut.rd.value = 5
    dut.wd.value = 0xAAAAAAAA
    dut.RegWrite.value = 0
    await settle()
    await RisingEdge(dut.clk)
    await settle()
    await check_read(5, 2, 0, model[2], "directed no write when RegWrite=0")

    # 7) Reset clears everything
    await apply_reset()
    model = [0] * 32
    await check_read(1, 31, 0, 0, "directed reset clears regs")

    # 8) Rebuild a small state after reset
    await write_reg(7, 0x11111111)
    model[7] = 0x11111111
    await write_reg(8, 0x22222222)
    model[8] = 0x22222222
    await write_reg(9, 0x33333333)
    model[9] = 0x33333333
    await check_read(7, 8, model[7], model[8], "directed post-reset write")
    await check_read(9, 0, model[9], 0, "directed post-reset x0 read")

    # 9) Exhaustive interface readback
    for r in range(32):
        got1, _ = await read_regs(r, 0)
        exp = 0 if r == 0 else model[r]
        assert got1 == exp, (
            f"[directed exhaustive] x{r} expected=0x{exp:08X}, got=0x{got1:08X}"
        )

    # -------------------------
    # Randomized tests
    # -------------------------
    random.seed(12345)

    for i in range(500):
        op = random.choice(["write", "read", "reset"])

        if op == "reset" and random.random() < 0.08:
            await apply_reset()
            model = [0] * 32

            rs1 = random.randint(0, 31)
            rs2 = random.randint(0, 31)
            exp1 = 0 if rs1 == 0 else model[rs1]
            exp2 = 0 if rs2 == 0 else model[rs2]
            await check_read(rs1, rs2, exp1, exp2, f"rand {i} reset")
            continue

        if op == "write":
            rd = random.randint(0, 31)
            wd = random.getrandbits(32)

            await write_reg(rd, wd)

            if rd != 0:
                model[rd] = u32(wd)

            # check a random read pair after the write
            rs1 = random.randint(0, 31)
            rs2 = random.randint(0, 31)
            exp1 = 0 if rs1 == 0 else model[rs1]
            exp2 = 0 if rs2 == 0 else model[rs2]
            await check_read(rs1, rs2, exp1, exp2, f"rand {i} write")

        else:  # read
            rs1 = random.randint(0, 31)
            rs2 = random.randint(0, 31)
            exp1 = 0 if rs1 == 0 else model[rs1]
            exp2 = 0 if rs2 == 0 else model[rs2]
            await check_read(rs1, rs2, exp1, exp2, f"rand {i} read")

    # -------------------------
    # Final full readback
    # -------------------------
    for r in range(32):
        got1, _ = await read_regs(r, 0)
        exp = 0 if r == 0 else model[r]
        assert got1 == exp, (
            f"[final readback] x{r} expected=0x{exp:08X}, got=0x{got1:08X}"
        )

    logger.info("All register file tests passed!")