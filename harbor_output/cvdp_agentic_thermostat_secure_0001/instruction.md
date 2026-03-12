I have a **thermostat** module located at `code/rtl/thermostat.v`. This module currently lacks access control and can operate without any restriction. I want to enhance the system to be **secure**, such that the thermostat only functions after a proper unlock sequence has been successfully completed.

---

### **Modification Goals**

Create a new module, named "security_module" in file "security_module.v" that acts as a **security gatekeeper**. This module must implement a finite state machine that enforces an **unlock sequence** before enabling the thermostat. The unlock sequence consists of two steps:
1. First, the hexadecimal value `0xAB` must be written to internal address `0`.
2. Next, the value `0xCD` must be written to internal address `1`.

Only when both steps are performed in sequence should the system be considered **secure**. Any deviation (incorrect value or incorrect order) should cause the state machine to reset, requiring the entire sequence to be redone. The secure module is resettable and must return to the locked state upon system reset.

Once the unlock is complete, the secure module should assert a signal that enables the thermostat. Until then, the thermostat must remain inactive.

---

### **Top-Level Integration**

Create a new top-level module named "thermostat_secure_top.v" that integrates both the security module and the thermostat. Ensure correct data flow and signal connection between them.
Below are the IOs.

```verilog 
module thermostat_secure_top  #(
    parameter p_address_width = 8,                
    parameter p_data_width = 8,                  
    parameter p_unlock_code_0 = 8'hAB,            
    parameter p_unlock_code_1 = 8'hCD            
) (
    input wire [5:0] i_temp_feedback, 
    input wire i_fan_on,             
    input wire i_fault,              
    input wire i_clr,               
    input wire i_clk,                
    input wire i_rst,                
    input wire [p_address_width-1:0]   i_addr,             
    input wire [p_data_width-1:0]      i_data_in,          
    input wire                         i_read_write_enable, 
    input wire                         i_capture_pulse,    

    output reg o_heater_full,
    output reg o_heater_medium,
    output reg o_heater_low,
    output reg o_aircon_full,
    output reg o_aircon_medium,
    output reg o_aircon_low,
    output reg o_fan,
    output reg [2:0] o_state         
);
```

---

### **Clocks and Reset**

The secure module operates on a clock derived from a **capture pulse** signal, while the thermostat runs on its own **thermostat clock**. These clocks are asynchronous. The reset signal is shared across both modules. The top-level module must handle **clock domain crossing** between the two domains in a safe and reliable manner.

---

### **Expected Deliverable**

A complete design containing:
1. The **modified thermostat** that responds to a secure-enable condition.
2. A new **security module** enforcing the unlock logic.
3. A **top-level module** instantiating and integrating both components, managing control flow and asynchronous clocks.

The system must ensure that the thermostat never functions unless the unlock sequence is properly followed.
