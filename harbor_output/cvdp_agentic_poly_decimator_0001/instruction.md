You are required to design a System Verilog module `poly_decimator`. The `poly_decimator` is a top-module and it must integrate a number of provided files. The detailed specification of `poly_decimator` is provided in the document `docs/poly_decimator.md`.

## Integration Instructions
- The **`poly_decimator`** module, that should be defined in `rtl/poly_decimator.sv`, must serve as the top-level design. It is responsible for handling the overall decimation operation of M samples.

You are also provided with a library of pre-designed modules that must be integrated into the target module. The library modules are:

- **adder_tree**  
  - **Design File:** `rtl/adder_tree.sv`  
  - **Specifications:** `docs/adder_tree.md`  
  - **Functionality:** Implements a pipelined adder tree for summing multiple data inputs.

- **shift_register**  
  - **Design File:** `rtl/shift_register.sv`  
  - **Specifications:** `docs/shift_register.md`  
  - **Functionality:** Implements a shift register that stores a history of input samples.

- **coeff_ram**  
  - **Design File:** `rtl/coeff_ram.sv`  
  - **Specifications:** `docs/coeff_ram.md`  
  - **Functionality:** Provides a synchronous memory block for storing filter coefficients.

- **poly_filter**  
  - **Design File:** `rtl/poly_filter.sv`  
  - **Specifications:** `docs/poly_filter.md`  
  - **Functionality:** Implements the filtering operation for each polyphase branch: it multiplies a subset of input samples by the proper coefficients, then sums the products.

Ensure that you fully understand the functionality and interfaces of these modules as described in their specification documents. They must be integrated properly to achieve the desired polyphase decimation functionality
