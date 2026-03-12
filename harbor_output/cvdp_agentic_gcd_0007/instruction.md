Design a cryptographic accelerator that performs RSA-like encryption operations, details of which are given in the specification provided in the `docs` folder.
The required RTL files are present in the `rtl` folder, and their corresponding specifications are in the `docs` directory. Choose the appropriate RTL modules based on the descriptions given in the RTL specification documents, and create the System Verilog RTL module `crypto_accelerator` and add it to the `rtl` directory.
Use the existing module that calculates the GCD using Stein's algorithm (as described in the specification) to perform the check for coprimes. If the public exponent (e) and totient φ(n) are coprimes, then perform the encryption using the module that performs modular exponentiation of the inputs.

The existing modular_exponentiation provides incorrect output. Resolve the RTL issues in the module and update it.

Below is the port list of the `crypto_accelerator` module that you have to generate:
```verilog
module crypto_accelerator #(
    parameter WIDTH = 8
)(
    input                     clk,
    input                     rst,
    input      [WIDTH-1:0]    candidate_e,     // Candidate public exponent.
    input      [WIDTH-1:0]    totient,             // Euler's totient φ(n).
    input                     start_key_check,
    output logic              key_valid,
    output logic              done_key_check,
    input      [WIDTH-1:0]    plaintext,
    input      [WIDTH-1:0]    modulus,
    output logic [WIDTH-1:0]  ciphertext,
    output logic              done_encryption
);
```
