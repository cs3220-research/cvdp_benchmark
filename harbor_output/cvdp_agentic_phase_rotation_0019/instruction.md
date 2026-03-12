The original `phase_lut` module has `i_data_i` and `i_data_q` as inputs (each 6 bits wide) and `o_phase` as a 9-bit output. The output is generated based on the inputs, which are used to access an internal lookup table (LUT). For each pair of input values, the module produces an output using a `case` statement that covers all possible input combinations.

The **phase_lut** module must be updated with the following interface and internal behavior:

---

### Interface Modifications

- Add **2 input ports**:

  - A **clock input** for sequential logic: `clk`.
  - An **asynchronous active-low reset input**: `rst_async_n`.

- Add **2 new parameters**:
  - A parameter to define the number of **integer bits** in the input data (fixed value: `1`): `NBI_IN`.
  - A parameter to define the number of **integer bits** in the output phase (fixed value: `1`): `NBI_PHASE`.

- The existing parameters are fixed as:
  - Input width (`NBW_IN`): `6` bits.
  - Output width (`NBW_PHASE`): `9` bits.

---

### Derived Configuration (fixed values)

- The number of **fractional bits** in the inputs is `5`.
- The number of **fractional bits** in the output is `8`.

- The LUT will only store phase values corresponding to the **first quadrant** of the trigonometric circle.

- The LUT must have **1089 entries**, each representing a **normalized approximation of the arctangent function** between two positive fixed-point values.

- This number of entries is derived from all possible combinations of two 5-bit unsigned fractional values (representing the absolute values of the inputs), computed as:

  ```
  LUT_SIZE = 2^(2 × NBF_IN) + 2 × (2^NBF_IN) + 1
           = 2^10 + 2 × 2^5 + 1
           = 1024 + 64 + 1
           = 1089 entries
  ```

- These terms correspond to:
  - All combinations of I and Q: `2^10 = 1024`
  - Horizontal and vertical axis cases: `2 × 2^5 = 64`
  - One special case for zero input: `1`

---

### Combinational Logic

- Determine the **sign** of each input component.
- Compute the **absolute values** of both input components to map the vector into the first quadrant.
- Use a mathematical expression to generate a normalized index from the absolute values. This index must represent all combinations of two unsigned fixed-point numbers with `5` fractional bits each.
- Use this index to access a lookup table that contains **only the first-quadrant phase values**.
- With the signs previously captured, determine the **actual quadrant** of the original vector.
- Based on the quadrant, apply a **mathematical adjustment** to the LUT output:
  - If both components are **positive**, use the LUT value **directly**.
  - If the first component is **positive** and the second is **negative**, output the **negative** of the LUT value.
  - If the first component is **negative** and the second is **positive**, output the **difference between a full-scale constant and the LUT value**.
  - If both components are **negative**, output the **LUT value minus the full-scale constant**.

---

### Sequential Logic

- Register the calculated LUT index.
- Register the sign of each input component.
- On the rising edge of the clock, store these values to be used in the phase adjustment logic.
- On asynchronous reset (active low), all stored values must be cleared to `0`.

---

### LUT Construction

- The LUT must store precomputed values of the **arctangent function**, using only positive unsigned values for both input components.
- Each entry must be **normalized** to match the output format defined by the module parameters.
- The LUT can be generated using a fixed-point representation of the angle between two fractional inputs in the first quadrant.
- By using trigonometric symmetry, the LUT size is significantly reduced, and the output is reconstructed accurately across all four quadrants using simple transformations.

Unable to extract datapoint. Appear to have an binary file as part of the context/solution.
