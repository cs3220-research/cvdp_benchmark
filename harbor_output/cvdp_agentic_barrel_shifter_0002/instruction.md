Modify the barrel shifter module to support both logical and arithmetic shift modes and its current functionality (logical shift). The module should shift the input data based on the specified shift amount and direction while ensuring proper sign extension for arithmetic shifts. A new `shift_mode` input control signal should is also introduced to differentiate between logical and arithmetic shift modes.

---

### **Design Specification**

The `barrel_shifter` module is a digital circuit that shifts an input data word left or right by a specified amount. The module shall support arithmetic shift, in addition to the current logical shift functionality. The new control signal, `shift_mode`, selects the corresponding shift mode.

**Modes of Operation**
	1.	**Logical Shift (Default Behavior)**
	- When `shift_mode` = 0, the module performs a logical shift.
	-	For a logical left shift (LSL), zeroes (0s) are shifted into the least significant bits (LSBs).
	-	For a logical right shift (LSR), zeroes (0s) are shifted into the most significant bits (MSBs).
	2.	**Arithmetic Shift**
	-	When `shift_mode` = 1, the module performs an arithmetic shift.
	-	For an arithmetic right shift (ASR), the sign bit (MSB of the original data) is replicated into the vacated MSB positions to preserve the signed value.
	-	For an arithmetic left shift (ALSL), the behavior remains the same as a logical left shift (zeroes shifted into LSBs), since left shifts do not require sign extension.

**Shift Direction Control**
	-	`left_right` = 1: Left Shift (LSL or ALSL, depending on shift_mode)
	-	`left_right` = 0: Right Shift (LSR or ASR, depending on shift_mode)

### **Example Operations**

**Example 1: Logical Right Shift (LSR)**
-	**Input**:
  `shift_mode` = 0, `left_right` = 0, `shift_bits` = 3
  `data_in` = 8'b10110011
- **Expected Output**:
  `data_out` = 8'b00010110

**Example 2: Arithmetic Left Shift (ALSL)**
-	**Input**:
  `shift_mode` = 1, `left_right` = 1, `shift_bits` = 2
  `data_in` = 8'b10101001
- **Expected Output**:
  `data_out` = 8'b10100100 (Same as LSL, no sign extension needed)
