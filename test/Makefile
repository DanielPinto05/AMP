SIM ?= icarus

VERILOG_SOURCES += \
	$(PWD)/../src/alu_defs.sv \
	$(PWD)/../src/FSM.sv

COCOTB_TOPLEVEL = FSM
COCOTB_TEST_MODULES = test_FSM


include $(shell cocotb-config --makefiles)/Makefile.sim