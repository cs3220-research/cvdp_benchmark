Design a `digital stopwatch` module in SystemVerilog. Refer to the specification provided in `docs/digital_stopwatch_spec.md` to design the RTL. The specification details a parameterizable stopwatch that maintains seconds, minutes, and a single-bit hour indicator, along with a start/stop control. The design should be hierarchical, with dig_stopwatch_top as the top-level module and 
dig_stopwatch implementing the core stopwatch logic. It must include:

- A clock divider that generates a 1 Hz pulse from a parameterized input clock (default 50 MHz).
- Separate counters for seconds (0–59) and minutes (0–59).
- A single-bit hour signal that is asserted upon rolling over 59 minutes.
- Output signals to indicate pulses when second, minute, or hour counters change.
- A beep mechanism that activates on each hour pulse and deactivates on the next second pulse.

The code should be well-documented with clear comments explaining the functionality of each major block. Follow best practices in SystemVerilog coding to ensure readability, reusability, and maintainability.
