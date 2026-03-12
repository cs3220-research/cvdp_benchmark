Design a `direct_map_cache` module in SystemVerilog. Refer to the specification provided in `docs/direct_map_cache_spec.md` to design the RTL. The specification details a parameterizable direct-mapped cache supporting read/write operations, tag comparison for hit/miss detection, and valid/dirty bit management. Specifically, it must include:

## Requirements

1. **Parameterization**:
   - The design must be parameterizable for:
     - **Cache size**
     - **Data width**
     - **Tag width**
     - **Offset width**
   - This allows the design to scale easily to different systems.

2. **Tag Comparison Logic**:
   - Implement tag comparison logic to differentiate between cache hits and misses.

3. **Valid/Dirty Bit Management**:
   - Handle valid bit to mark cache lines as initialized or empty.
   - Track modifications using a dirty bit.

4. **Indexing and Offset Calculations**:
   - Address specific bytes within each cache line.
   - Include error detection for unaligned accesses.

5. **Synchronous Operations**:
   - Control read/write operations via the following signals:
     - `comp` (compare)
     - `write` (write)
     - `enable` (enable)

This document provides an overview of the `direct_map_cache` module design in SystemVerilog, outlining the key requirements, functionality, and design blocks.
