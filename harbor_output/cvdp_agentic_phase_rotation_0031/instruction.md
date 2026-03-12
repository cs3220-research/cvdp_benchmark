The **detect_sequence** module must be updated with the following changes to its interface and internal behavior.

#### Interface Modifications

- **Remove** the input signal `i_static_threshold` and its associated parameter.
- **Add** a new **parameter** `NBW_TH_UNLOCK`, default value: `3`.
- **Add** a new **input signal** `i_static_unlock_threshold` with width `NBW_TH_UNLOCK`.
- **Add** a new **1-bit output signal** `o_locked`.

#### Functional Description

- A new **finite state machine (FSM)** must be implemented with two operational states:
  - `ST_DETECT_SEQUENCE`: handles initial detection monitoring.
  - `ST_DETECT_PROC`: maintains a locked state and monitors detection quality.

- The FSM begins in the `ST_DETECT_SEQUENCE` state. While in this state, the module continuously evaluates incoming data for detection events. The signal responsible for defining the operation mode of the `correlate` module must be held low in this state, and the output `o_locked` must also remain low. A transition to the `ST_DETECT_PROC` state occurs only when both the output `o_proc_detected` is high and a signal returned from the `adder_2d_layer` module is high. This signal confirms that the detected values meet the criteria of being less than three valid modules.

- In the `ST_DETECT_PROC` state, the system assumes that detection has been achieved. A cycle counter begins tracking the number of processing cycles. If detection fails during a cycle (i.e., the detection output is low), a secondary counter increments to record consecutive failed sequences. The FSM transitions back to the `ST_DETECT_SEQUENCE` state when three conditions are met simultaneously: (1) the processing cycle counter reaches its maximum count, (2) no detection is reported, and (3) the failure counter reaches the value defined by the input `i_static_unlock_threshold`.

- While in `ST_DETECT_PROC`, if detection continues successfully, the FSM remains in this state, and the failure counter is reset. In this condition, the output `o_locked` is asserted high, and the mode selector for operation remains in its active configuration.

- The FSM uses an internal cycle counter to monitor the progress of a detection processing window. This counter increments on each valid cycle while the FSM is in the `ST_DETECT_PROC` state. When it reaches the predefined number of cycles that constitute a full processing window, the FSM evaluates detection outcomes and determines whether to maintain or exit the locked state.

- The output signal `o_locked` is asserted during the `ST_DETECT_PROC` state only when detection is actively being confirmed within the current processing window.

- Two counters are used by the FSM: one to count regular processing cycles and another to count undetected sequences. The regular processing cycle counter tracks the number of cycles processed during a locked window, and the undetected counter increments only when no detection occurs at the end of a window. Both counters must have a bit-width large enough to count up to the total number of 32-bit words defined in the external specification.

- The required counter size must accommodate a total number of words as specified in the `words_counting.md` document.

- All counters and state logic must respond to an asynchronous active-low reset (`rst_async_n`), which clears internal state and resets both counters.

- A condition influencing state transitions is provided by the `cross_correlation` module, which must be connected internally but requires no changes to that module's interface.

#### Cross Correlation Module Updates

- The **cross_correlation** module must be updated to include the following new interface signals:
  - An asynchronous active-low reset input (`rst_async_n`) received from the top-level.
  - A new input signal `i_mode`, which is provided by the FSM from the top-level module.
  - A new 1-bit output signal `o_aware_mode`, indicating internal awareness status.

- The `rst_async_n` and `i_mode` signals must be propagated internally to the **adder_2d_layers** submodule.
- Additionally, the `i_mode` signal must be connected to the **correlate** submodule.

These updates ensure consistent control and synchronization across internal components, and align the interface of the `cross_correlation` module with new detection and locking logic defined at the top level.

#### Adder 2D Layers Module Update

- The **adder_2d_layers** module must be modified to incorporate logic that monitors the value of the operation mode input.
- A new synchronous output flag must be raised when the mode input corresponds to a valid mode value.
- Valid mode values are defined externally and must be interpreted according to the list provided in the `valid_modes.md` document.
- This flag must be updated synchronously with the system clock and used to inform the FSM in the `detect_sequence` module that the current operation mode is valid.

#### Correlate Module Update

- The **correlate** module must be updated to support operation based on a new 2-bit input signal `i_mode`.
- When `i_mode` is set to `0`, the module should perform its original behavior without modification.
- When `i_mode` is set to `1`, all index computations must apply subtraction between relevant inputs.
- When `i_mode` is set to `2`, all index computations must apply addition between relevant inputs.
- When `i_mode` is set to `3`, the output indices must be forced to zero, effectively disabling dynamic computation.
