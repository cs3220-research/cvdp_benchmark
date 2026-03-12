Design a `continuous_adder` module in SystemVerilog within a file `continuous_adder.sv` at the location: `rtl/continuous_adder.sv`. Refer to the specification provided in `docs/continuous_adder_specification.md` and ensure you understand its content. The specification details the functionality of a configurable continuous accumulation adder with the following parameters:

- **DATA_WIDTH**: Configurable width of the input data.
- **ENABLE_THRESHOLD**: Enables or disables threshold-based accumulation.
- **THRESHOLD**: Defines the value at which the sum is considered complete.
- **REGISTER_OUTPUT**: Determines whether the output is registered.

The module processes incoming data by continuously accumulating values when `valid_in` and `accumulate_enable` signals are asserted. The accumulated sum is stored internally and can be flushed using the `flush` signal. If `ENABLE_THRESHOLD` is enabled and the accumulated sum reaches the specified `THRESHOLD`, the sum is output and the `sum_valid` signal is asserted.

### Functional Behavior

1. **Accumulation Logic:**  
   - Data is continuously added to an internal sum register when `valid_in` and `accumulate_enable` are high.
   - If `flush` is asserted, the sum register resets to zero.

2. **Threshold Handling:**  
   - If `ENABLE_THRESHOLD` is set, the module checks whether `sum_reg` has reached `THRESHOLD`.
   - When the threshold is met, the sum is output and `sum_valid` is asserted.

3. **Registering Output (Optional):**  
   - If `REGISTER_OUTPUT` is enabled, the `sum_out` and `sum_valid` outputs are updated synchronously with `clk` and `rst_n`.
   - If `REGISTER_OUTPUT` is disabled, `sum_out` and `sum_valid` are updated combinationally.

Generate the complete RTL code for the `continuous_adder`, ensuring optimized performance and compliance with the given specification.
