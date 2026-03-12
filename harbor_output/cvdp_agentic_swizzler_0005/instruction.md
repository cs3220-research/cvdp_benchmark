I have a **swizzler** module that performs complex cross-correlation and energy computation over input I/Q data. This module handles the internal processing logic required for computing correlation with conjugate reference sequences. It unpacks the input data into individual lanes, applies a swizzle map for remapping the lanes, detects invalid mappings, computes parity errors (if enabled), and finally performs a bit reversal on each lane before packing the data back into a flat output vector. The **swizzler** module is available at `/rtl/swizzler.sv` and its detailed specification is provided in the `/docs` directory.

Can you implement a top-level module called **`swizzler_supervisor`** ? The supervisor should integrate the **swizzler** module and augment its functionality with additional glue logic as described below.

The **swizzler_supervisor** module is designed to enhance the raw functionality of the **swizzler** subcomponent by:
  
- **Input Handling:**  
  - Pre-processing the input I/Q data to ensure proper formatting and conditioning prior to processing by the swizzler.
  - Applying potential reordering or scaling operations to align with the swizzler’s processing requirements.

- **Processing the Swizzler's Output:**  
  - Performing post-processing on the swizzler’s output, which includes computing a checksum across all lanes.
  - Comparing the computed checksum with a pre-defined expected value.
  - Generating error flags if a parity error, invalid mapping, or checksum mismatch is detected.
  - Applying additional bit manipulations (such as inverting the least significant bit in each lane) to produce the final data output.

- **Parameterization:**  
  - The design must be fully parameterizable to adapt to various configurations. Key parameters include:
    - **NUM_LANES**: Number of data lanes.
    - **DATA_WIDTH**: Bit-width of each lane.
    - **REGISTER_OUTPUT**: Option to pipeline outputs.
    - **ENABLE_PARITY_CHECK**: Toggle for parity error computation.
    - **OP_MODE_WIDTH**: Width of the operation mode signal.
    - **SWIZZLE_MAP_WIDTH**: Derived width for swizzle mapping.
    - **EXPECTED_CHECKSUM**: The checksum value against which the output is verified.

- **Error Supervision:**  
  - Integrate supervisory logic that validates the swizzler output by comparing the computed checksum with the expected value.
  - Assert a top-level error signal if any discrepancies arise (i.e., parity errors, invalid mapping errors, or checksum mismatches).

```verilog
module swizzler_supervisor #(
  parameter integer NUM_LANES           = 4,
  parameter integer DATA_WIDTH          = 8,
  parameter integer REGISTER_OUTPUT     = 1,
  parameter integer ENABLE_PARITY_CHECK = 1,
  parameter integer OP_MODE_WIDTH       = 2,
  parameter integer SWIZZLE_MAP_WIDTH   = $clog2(NUM_LANES)+1,
  parameter [DATA_WIDTH-1:0] EXPECTED_CHECKSUM = 8'hA5
)(
  input  wire                           clk,
  input  wire                           rst_n,
  input  wire                           bypass,
  input  wire [NUM_LANES*DATA_WIDTH-1:0] data_in,
  input  wire [NUM_LANES*SWIZZLE_MAP_WIDTH-1:0] swizzle_map_flat,
  input  wire [OP_MODE_WIDTH-1:0]         operation_mode,
  output reg  [NUM_LANES*DATA_WIDTH-1:0]  final_data_out,
  output reg                            top_error
);
  // [Internal implementation...]
endmodule
```

Please refer to `docs/swizzler_specification.md` for detailed design requirements and specifications of the subcomponent swizzler.
