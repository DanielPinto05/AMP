import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock


@cocotb.test()
async def ram_test(dut):
    """Test writing and reading from memory"""

    # 1. Start a 10ns period clock on the 'clk' pin
    clock = Clock(dut.clk, 1, unit="ns")
    cocotb.start_soon(clock.start())

    # 2. Reset / Initial Values
    dut.write_enable.value = 0
    dut.addr.value = 0
    dut.data_in.value = 0
    await RisingEdge(dut.clk)

    # 3. Write a value (0xA5) to address 4
    dut.addr.value = 4
    dut.data_in.value = 0xA5
    dut.write_enable.value = 1
    await RisingEdge(dut.clk)

    # write a bunch of values to it:
    write_out = [0xA5, 0x00, 0x11, 0x7B, 0x6F, 0x89, 0x77, 0xFF, 0x99, 0x10]
    dut.write_enable.value = 1
    for i in range(10):
        dut.addr.value = i * 4
        dut.data_in.value = write_out[i]
        await RisingEdge(dut.clk)
    dut.write_enable.value = 0

    # 4. Read it back
    for i in range(10):
        dut.addr.value = 4 * i
        await RisingEdge(dut.clk)
        await Timer(100, unit="ps")  # small wait for 'signals to settle'?
        assert (
            dut.data_out.value == write_out[i]
        ), f"Expected {write_out[i]}, got {dut.data_out.value}"

    dut._log.info("ram.sv passed ram.py test.")
