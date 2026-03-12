Modify the direct_map_cache module to implement a 2-way set associative cache with victim-way replacement and retain all current functionality (including tag comparison, write/read access, valid/dirty/error status, and LSB alignment error checking). The module should select between two cache ways during tag matches and use a victim policy for cache line replacement when both ways are valid but there is a miss. The modified module introduces a new internal victimway register to alternate replacement decisions in the absence of a direct match.

## Added/Modified Parameterization

- **N**: Number of ways per set. Default is 2 to implement a 2-way set-associative cache. its a local parameter 

## Design Modifications

### Associative Cache Structure

- Introduced 2-way set associativity by instantiating tag, data, valid, and dirty storage for two ways.
- A new internal `victimway` register implements a round-robin replacement policy on cache misses.
- Read and Write logic updated to probe both ways, handle hits/misses correctly, and update the correct way.
- Error signal continues to detect misaligned offset accesses, specifically when the LSB of the offset is high.
- Cache reset and enable handling behavior remains consistent but expanded for two-way state management.

### Hit and Miss Logic

- Hits can occur in either of the two ways, indicated by separate internal signals (`hit0`, `hit1`).
- A multiplexer selects outputs (`data_out`, `tag_out`, `valid`, `dirty`) from the correct way based on which way had a hit.

### Victim-Way Replacement Policy

- A `victim-way` register tracks which way to replace upon a miss if both ways are valid.
- On a cache miss and when both ways are valid, the victim way is used to store new data and the victim-way indicator toggles to ensure even usage of both ways.

### Misalignment Error Handling

- Continues to set the error signal high if the least significant bit of the offset is 1 (misaligned access).

## Behavioral Changes

### Operation Modes

1. **Compare Read** (`comp=1, write=0`):  
   - Checks for tag matches in both ways, updates output signals accordingly.

2. **Compare Write** (`comp=1, write=1`):  
   - Performs write if a match is found in either way or initiates victim-way replacement if a miss occurs.

3. **Access Read** (`comp=0, write=0`):  
   - Performs reads based on valid bits, without affecting victim-way tracking.

4. **Access Write** (`comp=0, write=1`):  
   - Writes data and tag inputs to both ways without victim logic engagement.

### Example Usage

#### Compare Write (Miss, Replacement)

- **comp = 1, write = 1**, `tag_in = <tag>`, `index = <idx>`, `valid_in = 1`, `data_in = <data>`, both ways valid, tag mismatch in both ways.
- Data is written into the current victim way, and the victim-way toggles for the next replacement.

#### Compare Read (Hit)

- **comp = 1, write = 0**, `tag_in = <tag>`, matching tag found in either way.
- `hit` is set high, and the correct `data_out` is returned from the matching way.
