Design a hierarchical **HDBN Encoder/Decoder module** in SystemVerilog according to the provided specification in `docs/specification.md`. The design should consist of a top-level module named **`hdbn_top`**, which instantiates two submodules: **`hdbn_encoder`** and **`hdbn_decoder`**. Ensure your implementation adheres strictly to the specification, including:

- Parameterized selection between HDB3 and HDB2 encoding (`encoder_type`).
- Configurable pulse active state (`pulse_active_state`).

The encoder module (`hdbn_encoder`) must:

- Register input digital data and encode it into bipolar pulses (`P` and `N`).
- Implement zero-counting logic to insert violations, preventing DC bias.
- Alternate pulse polarity correctly, considering violation conditions.

The decoder module (`hdbn_decoder`) must:

- Register incoming bipolar pulse inputs (`P` and `N`).
- Decode the bipolar pulses back into digital data.
- Detect and indicate encoding errors, including violations, simultaneous pulses, and excessive consecutive zeros.
