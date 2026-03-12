Modify the fixed_priority_arbiter module(`rtl/fixed_priority_arbiter.sv`) to support Active Grant Tracking, Manual Clear, and Enable Control.

## Functional Enhancements

1. **Enable Control**
   - Add a new input `enable`.
   - Arbitration logic must only operate when `enable` is high.
   - If `enable` is low, the outputs must retain their previous values.

2. **Manual Clear**
   - Add a new input `clear`.
   - When `clear` is asserted, all outputs (`grant`, `valid`, `grant_index`, and `active_grant`) must reset to their default values, similar to `reset`.

3. **Active Grant Tracking**
   - Add a new output `active_grant`.
   - This must reflect the current granted request index in binary format, even during priority override.

## Modified Interface

### Inputs
- `enable`: Arbiter enable control  
- `clear`: Manual clear control  

### Outputs
- `active_grant[2:0]`: Reflects the currently granted request index

---
