Design a SystemVerilog module named `control_fsm` that implements a five-state finite state machine (FSM) for managing the data and processing control flow of a signal processing system. The FSM operates based on various input signals such as enable, valid flags, failure detection, and timeout counters.

The design includes:

**Five-State FSM**:  
Define a sequential FSM with five operational states:
- `PROC_CONTROL_CAPTURE_ST`
- `PROC_DATA_CAPTURE_ST`
- `PROC_CALC_START_ST`
- `PROC_CALC_ST`
- `PROC_WAIT_ST`

State transitions must be based on a combination of control enable signals, counter values, and processing result flags.

**Asynchronous Reset and Clocking**:  
Implement the FSM driven by a rising edge clock and an asynchronous active-low reset (`rst_async_n`).

**Counter-Driven Logic**:  
Integrate two counters:
- A general-purpose counter that governs data capture and calculation phases.
- A timeout counter that tracks processing wait periods.

**Output Control Logic**:  
The outputs must be derived using combinational logic based on the current FSM state. 

For further details, refer to the specification in `docs/proc_fsm_spec.md`.
