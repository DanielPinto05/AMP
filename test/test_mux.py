import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from cocotb.types import LogicArray  # helpful for binary calculations
import logging
import random


MASK32 = 0xFFFFFFFF


def u32(x: int) -> int:
    return x & MASK32

@cocotb.test()
async def mux_test(dut):
    """Test using the Muxes"""
    """
    Works for either:
      - two_to_one_mux (signals: mx,a,b,out)
      - four_to_one_mux (signals: mx,a,b,c,d,out)
    """
    logger = logging.getLogger("mux_test")
    logger.setLevel(logging.INFO)  # otherwise INFO isn't logged (not important enough.)
    logger.info("Starting mux_test")

    # 2. Add a FileHandler if you want it saved to a file
    # 'a' means append, 'w' means overwrite each run
    file_handler = logging.FileHandler("mux_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:  # Prevent adding multiple handlers if test runs twice
        logger.addHandler(file_handler)

    async def settle():
        await Timer(1, unit="ns")
    
    vectors = [
            # mx, a, b, expected
            (0, 0x00000000, 0xFFFFFFFF, 0x00000000),
            (1, 0x00000000, 0xFFFFFFFF, 0xFFFFFFFF),
            (0, 0x12345678, 0xDEADBEEF, 0x12345678),
            (1, 0x12345678, 0xDEADBEEF, 0xDEADBEEF),
            (0, 0xAAAAAAAA, 0x55555555, 0xAAAAAAAA),
            (1, 0xAAAAAAAA, 0x55555555, 0x55555555),
        ]

    for i, (mx, a, b, exp) in enumerate(vectors):
        dut.mx.value = mx
        dut.a.value = a
        dut.b.value = b
        await settle()
        got = int(dut.out.value)
        assert got == u32(exp), (
            f"[2to1][directed {i}] mx={mx} a=0x{a:08X} b=0x{b:08X} "
            f"expected=0x{u32(exp):08X}, got=0x{got:08X}"
        )

    # select-change behavior
    dut.a.value = 0x0BADF00D
    dut.b.value = 0xCAFEBABE
    dut.mx.value = 0
    await settle()
    assert int(dut.out.value) == 0x0BADF00D
    dut.mx.value = 1
    await settle()
    assert int(dut.out.value) == 0xCAFEBABE

    # randomized tests
    for i in range(200):
        a = random.getrandbits(32)
        b = random.getrandbits(32)
        mx = random.randint(0, 1)
        exp = a if mx == 0 else b

        dut.a.value = a
        dut.b.value = b
        dut.mx.value = mx
        await settle()

        got = int(dut.out.value)
        assert got == u32(exp), (
            f"[2to1][rand {i}] mx={mx} a=0x{a:08X} b=0x{b:08X} "
            f"expected=0x{u32(exp):08X}, got=0x{got:08X}"
        )


    logger.info("All mux tests passed ✅")
