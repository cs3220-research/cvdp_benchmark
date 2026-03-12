Develop a Verilog-based **cache controller** for a **direct-mapped cache** that consists of **32 entries**, each storing a **32-bit word**. The controller must efficiently handle **read and write operations** issued by a **CPU**, interact with a **main memory module**, and ensure **coherence** between the cache and memory.

## Key Functional Requirements

### 1. Tag Comparison & Hit/Miss Detection
- The cache must store **5-bit tags** to identify unique memory blocks.
- The controller should check if the requested address matches a valid tag.
- A **hit** occurs when a valid tag is found in the cache; otherwise, it results in a **miss**.

### 2. Read Operation
- If a **cache hit** occurs, data should be provided to the CPU immediately.
- If a **cache miss** occurs, the controller must fetch the data from **main memory** and store it in the cache before responding to the CPU.

### 3. Write Operation (Write-Through Policy)
- The cache follows a **write-through** policy, meaning every write operation updates both the cache (if it contains the requested address) and the main memory simultaneously.
- Even on a cache miss, the data must be written to **main memory**.

### 4. Memory Interface
- The controller should interact with main memory using the **mem_address, mem_write, and mem_read_data** signals.
- Memory accesses must ensure proper timing by considering the **mem_ready** signal before fetching new data.

### 5. Cache Validity & Initialization
- The controller must initialize all cache entries as **invalid** upon reset.
- Each cache line must have a corresponding **valid bit** to indicate if it contains valid data.
