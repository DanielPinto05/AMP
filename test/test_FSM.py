import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
import logging


@cocotb.test()
async def test_FSM(dut):
    """Testing the FSM through some cycles"""

    logger = logging.getLogger("cocotb.test")  # Using the cocotb namespace
    # Create a file handler
    file_handler = logging.FileHandler("test_FSM.log", mode="w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    # Add the handler to the logger
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    logger.info("Starting test_FSM")

    # 1. Start a 10ns period clock on the 'clk' pin
    clock = Clock(dut.clk, 1, unit="ns")
    cocotb.start_soon(clock.start())

    # 2. set initial values

    await RisingEdge(dut.clk)
    dut.op.value = 0b0000000
    dut.funct7_5.value = 0
    dut.funct3.value = 0b000
    dut.reset.value = 0  #! mainly just testing that reset works
    await RisingEdge(dut.clk)

    logger.info(f"cycle 1: IRWrite = {dut.IRWrite.value}")
    await RisingEdge(dut.clk)

    # now IR write should transition to 1
    logger.info(f"cycle 2: IRWrite = {dut.IRWrite.value}")
    await RisingEdge(dut.clk)

    logger.info("Finished the null test.")
    dut._log.info("ran test with no output checks.")
