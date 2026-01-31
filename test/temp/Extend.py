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

    instr = LogicArray("111111111111xxxxxxxxxxxxx")  # just the 31:7 part
    expected = 0xFFFFFFFF
    dut.ImmSrc.value = 0b000  # I-type
    dut.instr.value = instr
    if dut.ImmExt == 0xFFFFFFFF:
        logger.info(f"Pass! Expected {expected:08x}, got {dut.instr.value:08x}")
    else:
        logger.error(f"Fail. Expected {expected:08x}, got {dut.instr.value:08x}")
