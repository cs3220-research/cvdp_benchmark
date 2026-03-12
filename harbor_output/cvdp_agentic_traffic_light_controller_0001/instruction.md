I have an `traffic_controller_fsm` module that controls a traffic light, located at `/rtl/traffic_light_controller.sv`.  
I want to modify the current design such that the light changes are driven by both short and long time intervals using the timer module, named `timer_module` in file `timer_module.sv` with below specification. Instantiate this timer module alongside the existing traffic-light FSM in a new top-level module, `traffic_light_controller_top` in file `traffic_light_controller_top.sv`.
The expected outcome is that short and long timing behaviors are cleanly separated into a new timer-based module, then integrated with the existing FSM in a new top-level design.

---

### **Timer Module Behavior**
- The timer module tracks two different intervals, a “short” duration and a “long” duration.  
- When a short-timer trigger becomes active, the module counts cycles until it reaches the short duration limit. At that moment, it raises a signal indicating the short interval has expired.  
- When a long-timer trigger becomes active, the module counts cycles until it reaches the long duration limit. At that moment, it raises a signal indicating the long interval has expired.  
- If neither trigger is active, both timers are idle (or reset), and no expiration indication is set.  
- When reset is asserted, all internal counters and any expired signals are cleared immediately.

---

### **Top-Level Integration**
- Connect the timer’s short and long triggers from the FSM, and feed the timer’s expiration signals back into the FSM to drive state transitions.  
- Pass the short and long duration thresholds (e.g., `SHORT_COUNT` and `LONG_COUNT`) from the top-level to the timer module.

### **TOP LEVEL IOs**
| **Port Name**             | **Direction** | **Bit Width**  | 
|---------------------------|---------------|----------------|
| `i_clk`                   | Input         | 1              |
| `i_rst_b`                 | Input         | 1              |
| `i_vehicle_sensor_input`  | Input         | 1              |
| `o_main`                  | Output        | 3              |
| `o_side`                  | Output        | 3              |
