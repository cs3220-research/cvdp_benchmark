Design a `signed_comparator` module in SystemVerilog within a file `signed_comparator.sv` at the location: `rtl/signed_comparator.sv`. Refer to the specification provided in `docs/signed_comparator_specification.md` and ensure you understand its content. The specification details the functionality of a configurable signed comparator with the following parameters:

- **DATA_WIDTH**: Configurable bit width of the input values.
- **REGISTER_OUTPUT**: Enables or disables registered output.
- **ENABLE_TOLERANCE**: Allows approximate equality comparison by considering a tolerance range.
- **TOLERANCE**: Defines the maximum absolute difference for approximate equality when `ENABLE_TOLERANCE` is enabled.
- **SHIFT_LEFT**: Left-shift amount applied to both input values before comparison.

The module takes two signed input values, `a` and `b`, and compares them to determine greater-than (`gt`), less-than (`lt`), and equal (`eq`) conditions. If `ENABLE_TOLERANCE` is enabled, values within the specified `TOLERANCE` range are treated as equal. Additionally, an optional `bypass` mode forces the equality output (`eq = 1`) regardless of the input values.

### Functional Behavior

1. **Input Preprocessing:**  
   - Both inputs `a` and `b` are left-shifted by `SHIFT_LEFT` bits before comparison.
   - A signed subtraction computes the difference `diff = a_shifted - b_shifted`.

2. **Equality with Tolerance:**  
   - If `ENABLE_TOLERANCE` is enabled, the absolute difference `abs_diff` is compared to `TOLERANCE`.
   - If `abs_diff <= TOLERANCE`, `eq` is asserted (`eq = 1`).

3. **Comparison Logic:**  
   - If `bypass` is active, `eq` is forced to `1`, and `gt` and `lt` are set to `0`.
   - If `enable` is asserted:
     - If `eq_tolerance` is met, `eq = 1`, `gt = 0`, `lt = 0`.
     - Otherwise, normal signed comparison is performed to set `gt`, `lt`, and `eq` accordingly.

4. **Registering Output (Optional):**  
   - If `REGISTER_OUTPUT` is enabled, the comparison results (`gt`, `lt`, `eq`) are updated synchronously on the clock edge.
   - If `REGISTER_OUTPUT` is disabled, the outputs are updated combinationally.

Generate the complete RTL code for the `signed_comparator`, ensuring optimized performance and compliance with the given specification.
