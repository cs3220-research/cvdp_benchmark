The **top_phase_rotation** module must be updated with the following changes to its interface and internal connections:

#### Interface Modifications

Add the following **4 new 1-bit input signals**:
- `i_bypass`
- `i_en_capture_data`
- `i_en_capture_cos_sin`
- `rst_async_n`

#### Functional Description

- **`i_en_capture_data`**:
  - Acts as a **data-gate** for the input signals `i_data_re` and `i_data_im`.
  - When low, the input data is held (not updated).
  - Introduce **one cycle of latency** for this gated data path.
  - Implement a **reset mechanism** using **`rst_async_n`** (active-low, asynchronous reset) to ensure that gated registers reset to `0`.

- **`i_en_capture_cos_sin`**:
  - This signal must be forwarded to the **`gen_cos_sin_lut`** module (the same input signal should be created on this module interface).
  - The **`gen_cos_sin_lut`** module must be made **sequential**, with a **1-cycle latency**.
  - On reset (`rst_async_n` asserted low), its output values must be cleared to `0`.

- **`rst_async_n`**:
  - Must be connected to the **`phase_rotation`** and **`gen_cos_sin_lut`** modules.
  - Inside those modules, all internal registers must be reset to `0` when `rst_async_n` is low (**asynchronous active-low reset**).
  - The **`rst_async_n`** input signal should be created on blocks interface.

- **`i_bypass`**:
  - Must be connected to the **`phase_rotation`** module (the same input signal should be created on this module interface).
  - Internally, the module must implement **combinational bypass logic**:
    - When `i_bypass == 1'b1`: forward input data directly to the output.
    - When `i_bypass == 1'b0`: perform the normal phase rotation operation.
    - Should be change only once per reset.
