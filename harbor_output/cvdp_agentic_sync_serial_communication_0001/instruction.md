Design an `sync_serial_communication` with binary to gray code conversion module in SystemVerilog. Refer to the specification provided in `docs/sync_serial_communication_spec.md` to implement the RTL. The specification describes a module that takes 64 bit input data input and performs various transmit & receive operations on it based on a 3-bit selection signal. It also requires generating a Gray-coded version of the receive data.

**1. Hierarchical Design**

- The top-level module is `sync_serial_communication_tx_rx`, integrating `tx_block`, `rx_block`, and `binary_to_gray_conversion`.
- `tx_block` (transmitter) serializes and transmits data.
- `rx_block` (receiver) deserializes the data.
- `binary_to_gray_conversion` converts the received binary data into Gray code.

**2. Functional Details**

- **`tx_block` (Transmitter):**

    - Serializes `data_in` based on `sel`.
    - Supports 8-bit, 16-bit, 32-bit, and 64-bit transmission.
    - Generates a serial clock .

- **`rx_block` (Receiver):**

    - Deserializes output of  `tx_block` and reconstructs `data_out`.
    - Uses a counter to track received bits.


- **binary_to_gray_conversion:**

    - Converts `data_out` to Gray code when `done` is asserted.

**3. Timing & Synchronization**

- The system is synchronous to `clk`, with a serial clock  for RX operations.
- Reset (`reset_n`) initializes registers and buffers.
- `done` is asserted upon completion of transmission/reception.

The code should be well-documented with clear comments explaining the functionality of each major block. Follow best practices in SystemVerilog coding to ensure readability, reusability, and maintainability.
