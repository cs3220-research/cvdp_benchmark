Modify the `universal_shift_register` module to expand its functionality by incorporating additional shift and bitwise operation capabilities while retaining its original functionality (including hold, shift, rotate, and parallel load operations). The module should now support arithmetic shifts, bitwise logical operations (AND, OR, XOR, XNOR), bit reversal, bitwise inversion, parity checking, zero detection, and overflow indication for shifts and rotations.
## Added/Modified  Inputs

- **[1:0] bitwise_op**: 2-bit input signal selects the bitwise logical operation.
- **en**: 1-bit Enable signal controls the register operation explicitly.
- **[2:0] op_sel**: Expanded from the previous 2-bit mode_sel to a 3-bit selector supporting additional modes:
     - 000: Hold (retain current value)
     - 001: Logical Shift (shift bits in/out)
     - 010: Rotate (rotate bits within the register)
     - 011: Parallel Load (load from input)
     - 100: Arithmetic Shift (shift with sign bit handling)
     - 101: Bitwise Logical Operations (AND, OR, XOR, XNOR)
     - 110: Bit Reversal (reverse bit order)
     - 111: Bitwise Inversion (invert all bits)

## Added/Modified Outputs:
- **Overflow**: 1-bit output that captures and outputs the bit shifted or rotated out during shift and rotate operations.
- **parity_out**: 1-bit output that computes and outputs the XOR of all bits in the register (parity checking).
- **zero_flag**: 1-bit output indicates when the register content is zero.
- **msb_out**: 1-bit direct output of the most significant bit of the register.
- **lsb_out**: 1-bit direct output of the least significant bit of the register.

## Design Modifications

### Expanded Operation Modes:

1. **Hold (000)**: Retains the current value in the register.
2. **Logical Shift (001)**: 
   - Right/Left shift controlled by `shift_dir`, using `serial_in` as input.
   - Overflow captures shifted-out bit.
3. **Rotate (010)**:
   - Right/Left rotate controlled by `shift_dir`.
   - Overflow captures rotated bit.
4. **Parallel Load (011)**: 
   - Loads the register directly from `parallel_in`.
5. **Arithmetic Shift (100)**:
   - Arithmetic shift right retains MSB.
   - Arithmetic shift left shifts in 0.
   - Overflow captures shifted-out bit.
6. **Bitwise Logical Operations (101)**:
   - Performs AND, OR, XOR, XNOR selected by `bitwise_op` against `parallel_in`.
7. **Bit Reversal (110)**:
   - Reverses the bit order of the register content.
8. **Bitwise Inversion (111)**:
   - Inverts all bits in the register.

### Behavioral Changes:
- The module behavior is expanded to include arithmetic shifts and bitwise logical operations while maintaining previous behaviors for existing operations.
- Overflow bit handling is clearly defined during shifts and rotations.
- Parity checking and zero detection provide additional status indicators based on the current register content.
- MSB (msb_out) provides the direct output of the register's most significant bit.
- LSB (lsb_out) provides the direct output of the register's least significant bit.
## Example Usage:

1. **Arithmetic Shift Left**:
   - `op_sel = 100`, `shift_dir = 1` (left), register shifts left logically, shifting in 0 from the right, capturing overflow bit from MSB.
   
2. **Bitwise XOR Operation**:
   - `op_sel = 101`, `bitwise_op = 10` (XOR), performs XOR between current register content and `parallel_in`.

3. **Bit Reversal**:
   - `op_sel = 110`, reverses the bit order of the current register content.
