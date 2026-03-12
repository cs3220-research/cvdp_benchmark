Design a `ttc_counter_lite` module in SystemVerilog within a file ttc_counter_lite.sv at the location:rtl/ttc_counter_lite.sv Refer to the specification provided in `docs/specification.md` and ensure you understand its content. The specification describes the functionality of a lightweight timer counter with optional interrupt support and configurable modes. It includes a description of the register interface, internal behavior, timing characteristics, and how the counter behaves in different configurations.

Generate the complete RTL code that implements the `ttc_counter_lite` module as described in the specification. The design must include:
- A 16-bit up counter  
- Configurable match and reload values  
- Support for interval and single-shot operation modes  
- Programmable prescaler
- An interrupt output that asserts when the counter reaches the match value and interrupt_enable is set  
- Read/write access to registers via a simplified AXI-like register interface
