I have a **Linear Feedback Shift Register (LFSR) module** at `rtl/lfsr_8bit.sv` and a **test bench** at `verif/lfsr_8bit.sv`. The testbench simulation shows **errors**, resulting in a test failure.

## Module Specifications

### RTL (rtl/lfsr_8bit.sv)
The **8-bit LFSR module** has the following characteristics:

#### Inputs:
- `clk`: Clock signal  
- `rst`: Reset signal (active high)  
- `seed`: 8-bit **user-defined initial seed**

#### Output:
- `lfsr_out`: 8-bit **LFSR output**

#### Internal Logic:
- On **reset**, the LFSR is initialized with the user-defined **seed** value.
- The feedback is generated using the polynomial:
```verilog
  lfsr_out = {lfsr_out[6:0], lfsr_out[7] ^ lfsr_out[5] ^ lfsr_out[4] ^ lfsr_out[3]};
```
- On every **clock edge**, the LFSR shifts and updates its state.

### Testbench (verif/lfsr_8bit.sv)
The testbench is designed to validate the correctness of the LFSR module.

#### Clock Generation
- A **10ns clock period** (`#5 clk = ~clk;`)

#### Stimulus and Self-Checking
- **Initialization**
- The LFSR is initialized with the **seed** (`8'b10101010`) on reset.
- **Functional Test**
- Runs the LFSR for **20 cycles**, updating an expected **shift register** with the same feedback polynomial.
- Compares `lfsr_out` against `expected_lfsr`.
- **Error Checking**
- If the expected and actual outputs **do not match**, it prints an error message:
  ```verilog
  $error("ERROR at cycle %d: Expected %b, Got %b", i, shift_reg, lfsr_out);
  ```

#### Waveform Dumping
- Creates a waveform dump (`lfsr_8bit.vcd`) for debugging.

## Issue Observed
The testbench simulation **reports mismatches** between the expected and actual LFSR outputs.  

Could you help debug and fix the RTL to ensure the LFSR operates correctly?
