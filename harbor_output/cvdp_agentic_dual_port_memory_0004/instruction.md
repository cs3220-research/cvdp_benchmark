Can you **modify the `dual_port_memory` module** to support **ECC-based error detection** using the **Hamming(7,4)** code, for a memory array that allows **independent dual-port access**?

---

###  Design Specification

---

### Dual-Port Architecture

The memory must support **true dual-port access** where:

- **Port A** is used for **write operations** using:  
  - `addr_a` (address)  
  - `data_in` ([3:0] data input)  
  - `we` (write enable)

- **Port B** is used for **read operations** using:  
  - `addr_b` (address)  
  - `data_out` ([3:0] data output)

- Both ports must operate **concurrently and independently**, provided they access **distinct addresses**. Address collision management is **handled by the testbench**, not internally.

---

###  ECC Encoding and Error Detection

This module integrates **Hamming(7,4)** logic, which includes 4 data bits and 3 parity bits:

- **Data bits**: `d[3:0]`  
- **Parity bits** (`p[2:0]` for `ECC_WIDTH=3`):
  - `p0 = d0 ^ d1 ^ d3`
  - `p1 = d0 ^ d2 ^ d3`
  - `p2 = d1 ^ d2 ^ d3`

####  Write Operation (`we == 1`):
- Compute the 3-bit **ECC parity code** from the 4-bit `data_in` using Hamming(7,4).
- Store the original `data_in` into `ram_data[addr_a]`.
- Store the computed ECC bits into `ram_ecc[addr_a]`.

####  Read Operation:
- Fetch both `data_word` and `ecc_word` from memory arrays at `addr_b`.
- Recompute ECC from `data_word`.
- Calculate **syndrome** using XOR: `syndrome = ecc_word ^ computed_ecc`.
- If `syndrome != 3'b000`, assert `ecc_error = 1`, else `ecc_error = 0`.
- Always output uncorrected `data_word` on `data_out`.

---

###  Memory Organization

- `ram_data`: Stores 4-bit words (default `DATA_WIDTH = 4`)
- `ram_ecc`: Stores 3-bit ECC codes (default `ECC_WIDTH = 3`)
- `MEM_DEPTH = 2 ** ADDR_WIDTH` (default `ADDR_WIDTH = 5`, so 32 entries)

---

###  Reset Behavior

On `rst_n == 0`:
- `data_out` is cleared to 0.
- `ecc_error` is cleared to 0.
- Contents of `ram_data` and `ram_ecc` are **not reset or modified**.

---

###  Interface Parameters

| Parameter     | Description                                          |
|---------------|------------------------------------------------------|
| `DATA_WIDTH`  | Width of input/output data (default: 4 bits)         |
| `ECC_WIDTH`   | Width of ECC code (default: 3 bits for Hamming)      |
| `ADDR_WIDTH`  | Width of the address bus (default: 5 bits)           |
| `MEM_DEPTH`   | Number of memory locations (2<sup>ADDR_WIDTH</sup>)  |

---

###  Functional Constraints

- All ECC codes must be computed using **Hamming(7,4)** parity logic.
- Only **single-bit error detection** is required using the `ecc_error` signal.
- No correction or masking is required — `data_out` always shows uncorrected data.
- No internal hazard detection is required — assume testbench avoids simultaneous read/write to same address.

---

###  Output Behavior

- On ECC match: `ecc_error = 0`, `data_out = valid data`
- On ECC mismatch (1-bit error detected): `ecc_error = 1`, `data_out = same (uncorrected) data`

---
