Design an `nbit_swizzling` with binary to gray code conversion module in SystemVerilog. Refer to the specification provided in `docs/nbit_swizzling_spec.md` to implement the RTL. The specification describes a parameterizable module that takes an n-bit input data vector and performs various **reversal** operations on it based on a **2-bit selection signal**. It also requires generating a Gray-coded version of the reversed data. 

**1. Parameterizable Data Width (default 64 bits)**  
   - The module must allow configuring its width for different bit sizes (e.g., 32, 64, 128 bits).  

 **2. 2-bit Selection (`sel`) for Reversal Operation**  
   - `00`: Reverse the entire input data.  
   - `01`: Split the input into two halves and reverse each half.  
   - `10`: Split the input into four quarters and reverse each quarter.  
   - `11`: Split the input into eight segments and reverse each segment.  
   - Any invalid selection should cause a default pass-through (i.e., `data_out` = `data_in`).

 **3. Gray Code Generation**  
   - After the data is reversed (based on the selected mode above), generate a Gray-coded version of the reversed output.

The code should be well-documented with clear comments explaining the functionality of each major block. Follow best practices in SystemVerilog coding to ensure readability, reusability, and maintainability.
