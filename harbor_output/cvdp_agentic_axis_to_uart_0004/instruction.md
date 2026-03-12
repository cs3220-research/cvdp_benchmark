Design a `uart_rx_to_axis` module in SystemVerilog. Refer to the specification provided in `docs/uart_rx_to_axis_specs.md` and ensure you fully understand its content. The specification details the module’s parameterization for clock frequency (`CLK_FREQ`), UART bit rate (`BIT_RATE`), word size (`BIT_PER_WORD`), optional parity (0 for none, 1 for odd, 2 for even), and configurable stop bits (`STOP_BITS_NUM`). It also describes the finite state machine (FSM) that controls the reception process through states such as IDLE, START, DATA, PARITY, STOP1, STOP2, and OUT_RDY. The module must interface with a serial UART input (`RX`), detect and sample the start bit, data bits (received LSB first), an optional parity bit, and stop bit(s); then reconstruct the parallel data and output it on an AXI-Stream interface (using `tdata`, `tuser` for parity error indication, and `tvalid`). Proper timing is achieved by using a clock counter computed with the formula:

```
Cycle_per_Period = (CLK_FREQ * 1,000,000) / BIT_RATE
```

Implement the full RTL code that handles:
- Detection of the start bit (using falling-edge detection),
- Sampling of the incoming bits according to the UART timing,
- Correct ordering of data bits using an appropriate shift register implementation,
- Parity computation and verification when enabled,
- Generation of AXI-Stream outputs with correct data (`tdata`), parity error flag (`tuser`), and valid strobe (`tvalid`),
- Proper reset behavior that returns the FSM to the IDLE state.
