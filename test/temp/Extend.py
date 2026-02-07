import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from cocotb.types import LogicArray  # helpful for binary calculations
import logging


@cocotb.test()
async def Extend_test(dut):
    """Test using the Immediate Extender"""
    # clock
    # clock = Clock(dut.clk, 1, unit="ns")
    # cocotb.start_soon(clock.start())
    # logger
    logger = logging.getLogger("Extend_test")
    logger.info("Starting Extend_test")
    logger.setLevel(logging.INFO)  # otherwise INFO isn't logged (not important enough.)

    # 2. Add a FileHandler if you want it saved to a file
    # 'a' means append, 'w' means overwrite each run
    file_handler = logging.FileHandler("Extend_test.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    if not logger.handlers:  # Prevent adding multiple handlers if test runs twice
        logger.addHandler(file_handler)

    logger.info("Starting Extend_test")

    # --- Tests ----
    # 1. I-type
    instr = 0b1111111111110000000000000  # just the 31:7 part
    expected = 0xFFFFFFFF
    dut.ImmSrc.value = 0b000  # I-type
    dut.instr.value = instr
    await Timer(500, unit="ps")  # give some time to actually get something meaningful
    assert dut.ImmExt.value == expected, logger.error(
        f"Expected {expected}, got {dut.ImmExt.value}."
    )

    # * Next: set everything up as test_vectors so we can go through all the different extension types
    # test_vectors =[(0xFFF00000, 0b000)]
    # for instr, type in test_vectors:

    logger.info(f"Pass. dut.ImmExt.value = {dut.ImmExt.value}")
