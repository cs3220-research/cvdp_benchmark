I have a **APBGlobalHistoryRegister** module located at `rtl/APBGlobalHistoryRegister.v`. This module currently lacks access control and can operate without any restriction. I want to enhance the system to be **secure**, such that the global history shift register only functions after a proper unlock sequence has been successfully completed.

---

### **Modification Goals**

Create a new module, named "security_module" in file "security_module.v" that acts as a **security gatekeeper**. This module must implement a finite state machine that enforces an **unlock sequence** before enabling the global history shift register. The unlock sequence consists of two steps:
1. First, the hexadecimal value `0xAB` must be written to internal address `0`.
2. Next, the value `0xCD` must be written to internal address `1`.

Only when both steps are performed in sequence should the system be considered **secure**. Any deviation (incorrect value or incorrect order) should cause the state machine to reset, requiring the entire sequence to be redone. The secure module is resettable and must return to the locked state upon system reset.

Once the unlock is complete, the secure module should assert a signal that enables the global history shift register. Until then, the global history shift register must remain inactive. Modify the "APBGlobalHistoryRegister" such that it will enable when the module is secure.

---

### **Top-Level Integration and module modification**

Create a new top-level module named "APBGlobalHistoryRegister_secure_top.v" that integrates both the security module and the global history shift register. Ensure correct data flow and signal connection between them. The security module interface should use the existing 8-bit apb interface but with a different clock named "i_capture_pulse". 
Below are the IOs.

```verilog 
module APBGlobalHistoryRegister_secure_top  #(                  
    parameter p_unlock_code_0 = 8'hAB,            
    parameter p_unlock_code_1 = 8'hCD            
) (
    input  wire         pclk,  
    input  wire         presetn,  
    // APB signals
    input  wire [9:0]   paddr,  
    input  wire         pselx,  
    input  wire         penable,  
    input  wire         pwrite, 
    input  wire [7:0]   pwdata, 
    input  wire         history_shift_valid,  
    input  wire         clk_gate_en,  
    
    input wire          i_capture_pulse,    

    output reg          pready, 
    output reg  [7:0]   prdata, 
    output reg          pslverr,  
    output reg          history_full, 
    output reg          history_empty,  
    output reg          error_flag, 
    output reg          interrupt_full, 
    output reg          interrupt_error       
);
```

---

### **Clocks and Reset**

The secure module operates on a clock derived from a **capture pulse** signal, while the global history shift register runs on its own **pclk clock**. These clocks are asynchronous. The reset signal is shared across both modules. 

---

### **Expected Deliverable**

A complete design containing:
1. The **modified global history shift register** that responds to a secure-enable condition.
2. A new **security module** enforcing the unlock logic.
3. A **top-level module** instantiating and integrating both components, managing control flow and asynchronous clocks.

The system must ensure that the global history shift register never functions unless the unlock sequence is properly followed.
