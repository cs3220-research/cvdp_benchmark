Create an `async_filo` module in SystemVerilog to implement a First-In-Last-Out (FILO) memory buffer with asynchronous read and write clock domains. Refer to the specification in `docs/spec.md`, which details the design requirements.

### The module must:

  - Support independent read and write clocks (r_clk and w_clk)
  - Be parameterized for data width and depth
  - Handle push and pop operations in a FILO manner
  - Safely synchronize read and write pointers across clock domains using Gray coding
  - Generate status flags:
    - `w_full`: asserted when the FILO is full from the write domain
    - `r_empty`: asserted when the FILO is empty from the read domain
