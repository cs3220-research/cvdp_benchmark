Develop a SystemVerilog-based `csr_apb_interface` that supports read and write access to internal control, data, and interrupt registers. The module must handle APB transactions using standard protocol signals (`pselx`, `penable`, `pwrite`) and expose register data through a 32-bit bus. It should also support interrupt status flag handling, write protection for specific registers, and expose the current FSM state via a debug output.

## **Key Functional Requirements**

### 1. APB Protocol Compliance
The module must support the AMBA APB protocol, managing read and write operations through the standard `pselx`, `penable`, and `pwrite` signals.  
All transactions must follow the three-phase handshake:  
**IDLE → SETUP → ACCESS**

### 2. Register Map and Access
The controller provides access to four key registers via the APB interface:

- DATA_REG (0x10):
  Holds `data1` (bits 19:10), `data2` (bits 9:0), and 12 bits of reserved data (31:20).

- CONTROL_REG (0x14): 
  Includes `enable`, `mode`, and 30 bits of reserved control fields.

- INTERRUPT_REG (0x18): 
  Stores interrupt enable bits: `overflow_ie`, `sign_ie`, `parity_ie`, and `zero_ie`, along with 28 reserved bits.

- ISR_REG (0x1C): 
  Holds interrupt status flags (`*_is`). These flags can be cleared by writing `1` to the corresponding enable bits in the `INTERRUPT_REG`.

### 3. FSM State Management
The design uses a finite-state machine with four states:

- IDLE:  
  Waits for `pselx` to be asserted.

- SETUP:
  Accepts and processes transaction requests, transitions to `READ_STATE` or `WRITE_STATE`.

- READ_STATE: 
  Outputs register data on `prdata` based on the address. Transitions back to `IDLE`.

- WRITE_STATE: 
  Writes data into registers from `pwdata`, with a protection mechanism for `ISR_REG` (writes are blocked). Transitions back to `IDLE`.

### 4. Write Protection Mechanism
The `ISR_REG` is write-protected. Any attempt to write to it should assert `pslverr`.  
Writes to `INTERRUPT_REG` can clear corresponding ISR bits by writing `1` to the enable flags.
