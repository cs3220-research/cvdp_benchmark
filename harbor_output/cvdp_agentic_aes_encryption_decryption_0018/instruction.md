Update `aes_enc_top` and `aes_dec_top` RTLs so that the CTR block cipher mode changes how it concatenates the IV with the counter. The first 16 bits should be the 16 MSB of the counter, the next 96 should be the bits [111:16] from the IV and the next 16 bits should be the 16 LSB from the counter. As an example:

- `IV = 128'h00112233445566778899aabbccddeeff` and `counter = 32'h55443322`, the combination of them (used in the input of the encryption module in both `aes_dec_top` and `aes_enc_top`) should be `enc_in = 128'h55442233445566778899aabbccdd3322`.

Also, create a new module that instantiates both `aes_enc_top` and `aes_dec_top` modules and uses them to perform encryption or decryption depending on the `i_encrypt` control signal. This module should add support for four different padding modes used in block ciphers. The testbench to validate this functionality is provided in the `verif` directory, and no other changes, besides those described above, are required in any other RTL. This new module is described below:

### Specifications

- **Module Name**: `padding_top` (defined in `rtl/padding_top.sv`)
- **Parameters**:
    - `NBW_KEY`: Bit width of the encryption/decryption key.
        - Default: 256.
        - Related interface signals: `i_key`.
    - `NBW_DATA`: Bit width of the input and output data blocks.
        - Default: 128.
        - Related interface signals: `i_data`, `o_data`, `i_iv`.
    - `NBW_MODE`: Bit width for cipher mode selection.
        - Default: 3.
        - Related interface signals: `i_mode`.
    - `NBW_CNTR`: Bit width of the counter (used in CTR mode).
        - Default: 32.
    - `NBW_PADD`: Bit width to represent padding length.
        - Default: 4.
        - Related interface signals: `i_padding_bytes`.
    - `NBW_PMOD`: Bit width to represent padding mode.
        - Default: 2.
        - Related interface signals: `i_padding_mode`.
    - `W3C_BYTE`: Byte used for W3C padding.
        - Default: 8'hAF.

### Interface signals

- **Clock** (`clk`): Synchronizes operation on the rising edge.
- **Asynchronous Reset** (`rst_async_n`): Active low. Resets internal registers including the padding mode.
- **Encryption Mode** (`i_encrypt`): When high, the encryption path is selected; otherwise, the decryption path is selected. It should remain at the desired value while configuring the IV, mode and resetting the counter, until the operation is done.
- **Padding Mode Update** (`i_update_padding_mode`): When high, updates the internal padding mode register with `i_padding_mode`.
- **Padding Mode Selection** (`[NBW_PMOD-1:0] i_padding_mode`): Selects the padding logic to apply.
- **Padding Byte Count** (`[NBW_PADD-1:0] i_padding_bytes`): Indicates how many bytes of the input should be padded.
- **Reset Counter** (`i_reset_counter`): Reset signal for CTR mode. It resets the internal counter.
- **IV Update** (`i_update_iv`): When high, updates internal IV register with `i_iv`.
- **IV Data** (`[NBW_DATA-1:0] i_iv`): Input initialization vector.
- **Mode Update** (`i_update_mode`): When high, updates the internal cipher mode register with `i_mode`.
- **Mode** (`[NBW_MODE-1:0] i_mode`): Indicates which cipher mode to use (e.g., ECB, CBC, etc.).
- **Key Update** (`i_update_key`): When high and `i_start` is asserted, updates the key.
- **Key** (`[NBW_KEY-1:0] i_key`): Encryption/decryption key.
- **Start Operation** (`i_start`): Triggers encryption or decryption depending on `i_encrypt`.
- **Input Data** (`[NBW_DATA-1:0] i_data`): The plaintext or ciphertext block to be processed.
- **Done** (`o_done`): Indicates operation completion.
- **Output Data** (`[NBW_DATA-1:0] o_data`): The processed (encrypted or decrypted) data block.

### Internal Behavior

- The internal padding mode register is updated sequentially when `i_update_padding_mode` is high. It is cleared asynchronously when `rst_async_n` is low.
- The padding logic is combinational and modifies the least significant bytes of the input data block according to the selected padding mode.
- No padding is done when `i_padding_bytes == 0`, regardless of the selected padding mode.
- Given that the **Input Data** `i_data` is a fixed size (16 bytes), the padding is done by replacing the least significant bytes, instead of adding them (assuming that those bytes marked for padding are invalid in the input data).
- Since the **Padding Byte Count** is at most 15, the 16th byte of the **Input Data** will never be padded. The **Padding Byte Count** is limited to 15 given that for the 16th byte to be padded, the padding byte count should be 16 (which, again, is not allowed), and no data would be encrypted/decrypted, only the padding.
- The `aes_enc_top` used only when `i_encrypt == 1`.
- The `aes_dec_top` used only when `i_encrypt == 0`.
- Control signals like `i_update_iv`, `i_update_mode`, `i_update_key`, `i_reset_counter`, and `i_start` are gated so only the selected AES module receives them.

### Supported Padding Modes

- **PKCS#7** (`PKCS = 2'b00`):
    - Each padding byte is filled with the number of padding bytes.
    - Example: If 2 bytes are padded, both are `8'h02`.

- **One-And-Zeroes** (`ONEANDZEROES = 2'b01`):
    - First padding byte(most significant) is `8'h80`, remaining padded bytes are `8'h00`.

- **ANSI X9.23** (`ANSIX923 = 2'b10`):
    - All padding bytes are `8'h00`, except the last one(least significant), which contains the number of padded bytes.

- **W3C** (`W3C = 2'b11`):
    - All padding bytes are filled with the `W3C_BYTE` parameter (default is `8'hAF`), except the last one which contains the number of padded bytes.
