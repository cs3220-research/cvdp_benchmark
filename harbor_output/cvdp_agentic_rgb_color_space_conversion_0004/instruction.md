The existing RTL module `rgb_color_space_conversion` (located in the `rtl/` directory) currently supports RGB to HSV and HSL color space conversions. This module is implemented using pipelined and fixed-point arithmetic and receives 8-bit RGB inputs. Modify the module to include **CMYK (Cyan, Magenta, Yellow, Key/Black)** conversion logic, while maintaining existing HSV/HSL functionality and preserving pipeline structure. The CMYK conversion behavior, equations, and fixed-point scaling details are defined in the specification available in the `docs/` directory.

### **New Port Additions**

Add the following CMYK-specific output ports to the `rgb_color_space_conversion` module:

| Port Name             | Direction | Width     | Description                              |
|-----------------------|-----------|-----------|------------------------------------------|
| `cmyk_channel_c`      | Output    | 16-bit    | Cyan component in fx8.8 format.          |
| `cmyk_channel_m`      | Output    | 16-bit    | Magenta component in fx8.8 format.       |
| `cmyk_channel_y`      | Output    | 16-bit    | Yellow component in fx8.8 format.        |
| `cmyk_channel_k`      | Output    | 8-bit     | Black (Key) component in Integer format. |


### **Functional and Timing Constraints**

- CMYK logic should be pipelined and operate in parallel with existing HSV and HSL paths.
- All CMYK outputs (`cmyk_channel_c`, `cmyk_channel_m`, `cmyk_channel_y`, `cmyk_channel_k`) should align with `valid_out`, i.e., be valid in the same cycle as HSV and HSL outputs.
- Ensure proper reset behavior: all CMYK outputs should be cleared to `0` on reset.


### **Assumptions & Notes**

- The inputs (`clk`, `rst`, `valid_in`, `r_component`, `g_component`, `b_component`) remain unchanged until `valid_out` is HIGH.
- You may reuse the existing multi-port RAM for reciprocal lookup (i.e., 1 / i_max).
- Intermediate CMY computations may be staged across multiple clock cycles.
