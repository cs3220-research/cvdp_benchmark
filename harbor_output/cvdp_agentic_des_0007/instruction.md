Integrate the `des_enc` and `des_dec` modules to perform the Triple Data Encryption Standard (TDES) decryption. This new module must not allow burst operations; instead, it must perform start/done controlled operations, where whenever a start occurs, the done signal must be de-asserted, and any data, key, or start signals are ignored until the done signal is asserted again. A testbench for this new module is available at `verif/tb_3des_dec.sv`.

Also, update the `des_enc` and `des_dec` so that the `o_valid` signal from their interface and all logic related to them are removed, and `i_valid` input signal is renamed to `i_start`.

---

## Specifications

- **Module Name**: `des3_dec`

- **File Name**: `des3_dec.sv` (to be added in `rtl` directory)

- **Parameters**:
    - `NBW_DATA`: Bit width of the input and output data blocks.
        - Default: 64.
        - Related interface signals: `i_data`, `o_data`.
    - `NBW_KEY`: Bit width of the key.
        - Default: 192.
        - Related interface signal: `i_key`.  
        - The 192-bit key is interpreted as three concatenated 64-bit DES keys (K1, K2, K3) used for Triple DES decryption, where `K1 = i_key[1:64]`, K2 = `i_key[65:128]`, and `K3 = i_key[129:192]`.

- **Functionality**: Implements 3DES decryption in DED (Decrypt-Encrypt-Decrypt) mode using three 64-bit keys (K3, K2, K1). The input ciphertext is decrypted with K3, encrypted with K2, and decrypted again with K1.

- **Latency**: The block's latency, from when `i_start` is read until `o_done` is asserted, is **48 cycles**, where each DES stage takes 16 cycles.

---

## Interface Signals

  | Signal              | Direction | Width            | Description                                                                                                                           |
  |---------------------|-----------|------------------|---------------------------------------------------------------------------------------------------------------------------------------|
  | `clk`               | Input     | 1                | Drives the sequential logic on the rising edge.                                                                                       |
  | `rst_async_n`       | Input     | 1                | Active-low asynchronous reset; clears all internal registers and state.                                                               |
  | `i_start`           | Input     | 1                | Active high. Indicates that `i_data` and `i_key` are valid and ready to be processed.                                                 |
  | `i_data`            | Input     | [1:NBW_DATA]     | 64-bit ciphertext input block (MSB-first).                                                                                            |
  | `i_key`             | Input     | [1:NBW_KEY]      | 192-bit 3DES key, treated as three concatenated 64-bit keys: `{K1, K2, K3}`.                                                          |
  | `o_done`            | Output    | 1                | Asserted high when `o_data` contains valid encrypted data. It remains asserted until a new `i_start` signal is received.              |
  | `o_data`            | Output    | [1:NBW_DATA]     | 64-bit plaintext output block (MSB-first). After the decryption is calculated, it must remain stable until a next decryption is done. |
