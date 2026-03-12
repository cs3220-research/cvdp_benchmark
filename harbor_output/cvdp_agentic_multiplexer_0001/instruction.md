Design a `multiplexer` module in SystemVerilog within a file `multiplexer.sv` at the location: `rtl/multiplexer.sv`. Refer to the specification provided in `docs/multiplexer_specification.md` and ensure you understand its content. The specification details the functionality of a configurable multiplexer with the following parameters:

- **DATA_WIDTH**: Configurable data width of inputs.
- **NUM_INPUTS**: Number of input channels.
- **REGISTER_OUTPUT**: Option to register the output for pipelining.
- **HAS_DEFAULT**: Determines if a default value is used when `sel` exceeds `NUM_INPUTS`.
- **DEFAULT_VALUE**: The default output value when `HAS_DEFAULT` is enabled.

The module takes a `clk` and `rst_n` signal for synchronous reset behavior. It selects one of the `NUM_INPUTS` data inputs based on `sel`. If `bypass` is high, it forces `out` to always select `inp_array[0]`. The output is either combinational or registered based on `REGISTER_OUTPUT`.

Generate the complete RTL code that implements the `multiplexer` with the described behavior, ensuring that the code is optimized for performance and area efficiency.
