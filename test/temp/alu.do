vlib work

vlog src/ALU.sv

radix dec
vsim ALU
log {/*}
add wave {/*}

force a 32'd1
force b 32'd151
force ALUctrl 4'b0001
run 3ns