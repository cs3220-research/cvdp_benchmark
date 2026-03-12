I have a module named `event_scheduler` in the rtl directory that implements a programmable event scheduler for real-time systems. The original module supports dynamic event addition and cancellation by maintaining arrays of timestamps, priorities, and validity flags for up to 16 events. It increments an internal system time by a fixed step of 10 ns each clock cycle and triggers events when their scheduled time is reached. When multiple events are eligible, it selects the one with the highest priority. The module also signals an error if an event is added to an already active slot or if an attempt is made to cancel a non-existent event.

Your task is to modify the existing SystemVerilog code to enhance the functionality of the event scheduler while retaining the original interface ports. The modified module should still be named event_scheduler and remain in the same file (`rtl/event_scheduler.sv`). The specification detailing the architecture of the modified RTL is available in `docs` directory


**The modifications must include the following new features**:

## Event Modification/Rescheduling:

Add a new control input called `modify_event` and two additional inputs: `new_timestamp` and `new_priority.

When `modify_event` is asserted, the module should update the timestamp and priority for an existing event (identified by `event_id`), provided that the event is already active.

The module must assert the error signal if the event is inactive.

## Recurring Events:

Introduce two new inputs: `recurring_event` (a flag) and `recurring_interval` (a 16-bit value).

If an event is marked as recurring (i.e. recurring_event is high), then when that event is triggered, its timestamp should be automatically updated by adding the recurring_interval rather than deactivating the event.

This feature allows the scheduler to support periodic events.

## Event Logging:

Add two new outputs: `log_event_time` and `log_event_id`.

These outputs should capture the system time at which an event is triggered and the corresponding event ID.

The logging must occur in the same cycle as the event trigger.

## Additional requirements:

The modified module must retain the original interface for `clk`, `reset`, `add_event`, `cancel_event`, `event_id`, `timestamp`, and `priority_in`.

All additional functionality must be added by introducing extra inputs and outputs without altering the existing ones.

The design must continue to increment the internal `current_time` by 10 ns per cycle and use temporary arrays for atomic updates.

The error handling should remain intact: the module must assert an error if a duplicate event addition is attempted or if a modification/cancellation is attempted on a non-existent event.

The selection logic should continue to choose the highest priority event among those that are due, based on the updated time.

The module should update all temporary state and then commit the changes at the end of the clock cycle to ensure proper synchronization.

## Deliverable :
Your deliverable is the modified SystemVerilog code in the file `rtl/event_scheduler.sv` that implements these enhancements while maintaining similar timing characteristics and behavior as the original design.
