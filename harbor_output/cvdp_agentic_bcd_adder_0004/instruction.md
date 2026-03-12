Modify the existing single-digit BCD adder module to support multi-digit BCD addition, subtraction, and comparison. The updated design introduces parameterized modules that process N-digit BCD numbers by chaining single-digit BCD arithmetic. A top-level module is added to perform subtraction-based comparisons using reusable arithmetic logic. Update the `bcd_adder` module to include a `cin` (carry-in) input for chaining, remove invalid input checks (delegating it to higher-level module), and focus solely on single-digit BCD addition with proper decimal correction.

## Design Overview

### Key Modules

1. **bcd_adder**
   - Include a carry-in (`cin`) input for chaining multiple `bcd_adder` blocks in multi-digit designs.
   - Remove invalid output checks (`invalid`) to simplify the module; higher-level modules (like `multi_digit_bcd_add_sub`) must ensure valid BCD input.
   - Focus on single-digit BCD addition with decimal correction—no direct subtraction or invalid input logic.

2. **multi_digit_bcd_add_sub**  
   - Handles N-digit BCD addition and subtraction.
   - Operates on digit-by-digit BCD values (4 bits per digit).
   - Supports both modes of operation: addition and subtraction (9's complement for subtraction).
   - Carries or borrows are propagated between digits.

3. **bcd_top**  
   - Compares two N-digit BCD values using subtraction-based logic by instances of `multi_digit_bcd_add_sub`.
   - Determines if `A` is less than, equal to, or greater than `B`.

### Parameters:
- **N**: Defines the number of BCD digits to process, with a default value of 4. This must be a positive integer greater than or equal to 1.

---

## Module Specifications

### **Single-Digit Arithmetic Module: `bcd_adder`**

**Inputs**
- `a[3:0]`: A single Binary-Coded Decimal (BCD) digit (4-bit).
- `b[3:0]`: A single Binary-Coded Decimal (BCD) digit (4-bit).
- `cin`: A single-bit carry-in for the addition.

**Outputs**

- `sum[3:0]`: The 4-bit BCD sum of the two input digits.
- `cout`: A single-bit carry-out, which indicates an overflow beyond the valid BCD range (i.e., when the result exceeds 9).

**Functionality**
- Adds two 4-bit BCD digits (a and b) along with an optional carry-in (cin).
- Corrects the raw binary sum to produce a valid BCD digit (sum).
- Generates a carry-out (cout) to handle overflow when the resulting sum exceeds 9 in decimal.

---

### **Multi-Digit Arithmetic Module: `multi_digit_bcd_add_sub #(parameter N = 4)`**

**Inputs**  
- `A[4*N-1:0]`: N-digit Binary-Coded Decimal (BCD) input, with each digit represented as a 4-bit binary value 
- `B[4*N-1:0]`: N-digit Binary-Coded Decimal (BCD) input, with each digit represented as a 4-bit binary value 
- `add_sub`: 1-bit Operation selection signal. A high signal (1) selects addition, and a low signal (0) selects subtraction.

**Outputs**  
- `result[4*N-1:0]`: N-digit Binary-Coded Decimal (BCD) result of the operation, each digit represented as a 4-bit binary value
- `carry_borrow`: Single-bit output that indicates a carry-out from addition or a borrow-out from subtraction.

**Functionality**  
- Performs digit-wise BCD arithmetic using instances of `bcd_adder`.
- Carries or borrows are passed between digits.
- In subtraction mode, it automatically handles 9’s complement conversion and the initial carry-in.

---

### **Top-Level Module: `bcd_top #(parameter N = 4)`**

**Inputs**  
- `A[4*N-1:0]`: N-digit Binary-Coded Decimal (BCD) input, with each digit represented as a 4-bit binary value
- `B[4*N-1:0]`: N-digit Binary-Coded Decimal (BCD) input, with each digit represented as a 4-bit binary value

**Outputs**  
- `A_less_B`: Single-bit output is high when A is less than B; otherwise, it remains low.  
- `A_equal_B`: Single-bit output is high when A is equal to B; otherwise, it remains low.
- `A_greater_B`:  Single-bit output is high when A is greater than B; otherwise, it remains low.

**Functionality**  
- Performs subtraction of `A - B` using instances of `multi_digit_bcd_add_sub`.
- Uses the result and the final borrow output to determine comparison flags.



---

## Example Operations

### Example 1: `A Less Than B`

**Input**  
- `A = 8'b00100101`  // BCD for 25  
- `B = 8'b00111000`  // BCD for 38

**Expected Output**  
- `A_less_B = 1`  
- `A_equal_B = 0`  
- `A_greater_B = 0`

### Example 2: `A Equal to B`

**Input**  
- `A = 8'b01000101`  // BCD for 45  
- `B = 8'b01000101`  // BCD for 45

**Expected Output**  
- `A_less_B = 0`  
- `A_equal_B = 1`  
- `A_greater_B = 0`

### Example 3: `A Greater Than B`

**Input**  
- `A = 8'b01010010`  // BCD for 52  
- `B = 8'b00111001`  // BCD for 39

**Expected Output**  
- `A_less_B = 0`  
- `A_equal_B = 0`  
- `A_greater_B = 1`

---
