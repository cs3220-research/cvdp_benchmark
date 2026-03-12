Create a module that implements the **Data Encryption Standard (DES)** encryption algorithm. This module performs bit-accurate DES encryption on a 64-bit plaintext block using a 64-bit key. The module must support synchronous encryption with a valid interface. It must suport burst operation, where `i_valid` is asserted for multiple cycles in a row. A testbench, `tb_des_enc.sv`, file is provided to test this new module. The description and requirements for the module are provided below:

---

## Specifications

- **Module Name**: `des_enc` (to be added in `rtl` directory)

- **Parameters**:
    - `NBW_DATA`: Bit width of the input and output data blocks.
        - Default: 64.
        - Related interface signals: `i_data`, `o_data`.
    - `NBW_KEY`: Bit width of the key.
        - Default: 64.
        - Related interface signals: `i_key`.
- **Latency**: The block's latency, from when `i_valid` is read until `o_valid` is asserted, must be equal to the number of rounds: 16 cycles.

---

## Interface Signals

| Signal              | Direction | Width            | Description                                                                                                            |
|---------------------|-----------|------------------|-------------------------------------------------------------------------------------------------------------------     |
| `clk`               | Input     | 1                | Drives the sequential logic on the rising edge.                                                                        |
| `rst_async_n`       | Input     | 1                | Active-low asynchronous reset; clears all internal registers and state.                                                |
| `i_valid`           | Input     | 1                | Active high. Indicates that `i_data` and `i_key` are valid and can be processed.                                       |
| `i_data`            | Input     | [1:NBW_DATA]     | 64-bit plaintext input block (MSB-first).                                                                              |
| `i_key`             | Input     | [1:NBW_KEY]      | 64-bit encryption key.                                                                                                 |
| `o_valid`           | Output    | 1                | Asserted high when `o_data` contains valid encrypted data. It is asserted for as many cycles as `i_valid` is asserted  |
| `o_data`            | Output    | [1:NBW_DATA]     | 64-bit ciphertext output block (MSB-first).                                                                            |
---

## Internal Behavior

In this module description, the first `n` bits of a value declared as [1:NBW] are `1, 2, 3, ... , n-1, n`, and the last `n` bits are `NBW-(n-1), NBW-(n-2), ... , NBW-1, NBW`.

The `des_enc` module implements the standard **16-round Feistel structure** of DES. The process is divided into the following stages:

### 1. Initial Permutation (IP)

The 64-bit input block undergoes a fixed initial permutation. The description for this step is available at the "Permutations.md" file.

The first 32 bits are stored in $`L_0`$ and the last 32 bits in $`R_0`$.

---

### 2. Key Schedule

- The 64-bit input key is reduced to 56 bits via a **parity drop**.
- It is then split into two 28-bit halves.
- Each half is rotated left based on a fixed schedule per round.
- A **PC-2** permutation compresses the result to 48-bit round keys (`K1` to `K16`).

The "Key_schedule.md" file describes this operation in more detail.

---

### 3. Feistel Rounds

Each of the 16 rounds updates the left and right halves as follows:

$`L_n = R_{n-1}`$

$`R_n = L_{n-1} ⊕ F(R_{n-1}, K_n)`$

Where `F` is the round function consisting of:

- **Expansion (E)**: Expands 32-bit R to 48 bits using a fixed table. Described in the "Permutations.md" file.
- **Key Mixing**: Uses the expanded value from the **Expansion (E)** operation and XORs it with the 48-bit round key $`K_n`$.
- **S-box Substitution**: 48 bits are split into 8 groups of 6 bits, passed through S-boxes S1–S8. Each S-box is a 4x16 table (64 entries) mapping a 6-bit input to a 4-bit output. Those operations are described in the "S_box_creation.md" file.
- **Permutation (P)**: 32-bit output of S-boxes is permuted via a fixed permutation. Described in the "Permutations.md" file.

---

### 4. Final Permutation (FP)

After the 16th round, the L and R halves are concatenated in reverse order and passed through the **Final Permutation**, which is the inverse of IP. This concatenation is described in the "Permutations.md" file.

---

## Substitution box files

To perform the operations S1, S2, ... , S8 described in "S_box_creation.md"; create the files `S1.sv`, `S2.sv`, `S3.sv`, `S4.sv`, `S5.sv`, `S6.sv`, `S7.sv`, `S8.sv` and place them at the `rtl` directory.
