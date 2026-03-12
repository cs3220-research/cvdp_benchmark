The `event_storage` module in rtl directory synchronously stores events from the input `i_event` in a register bank. Each `i_event` input has an equivalent register. If the interface signal `i_en_overflow` is asserted, the register bank may wrap around when it reaches its maximum value, and an event occurs. If not asserted, the data stored in the register bank must be saturated.

The signals `i_bypass`, `i_data`, `i_raddr` are used to set the `o_data` signal such as:
- If `i_bypass == 1`, then `o_data = i_data`.
- If `i_bypass == 0`, then `o_data = reg_bank[i_raddr]`.

**Modify** the module `event_storage` so that it is fully parameterizable. The parameters for this block are:

- `NBW_STR`: Defines the bit width of the input and output data, as well as the bit width of each register in the register bank.
- `NS_EVT`: Defines the number of parallel events stored by the module.
- `NBW_EVT`: Defines the bit width of the read address used to select one of the event counters in `reg_bank`.

----------

The `event_array` module implements a **2D pipeline of event processors** (called `event_storage` units), structured as a grid of **NS_ROWS × NS_COLS**. Each processor operates on a stream of input data and associated events, performing updates and passing data to the next row in the same column. **All of the top module connections are fully combinational**. A testbench for it is provided.

**Create** an `event_array` module in the rtl directory, and make sure it is fully parameterizable.

### Specifications

- **Module Name**: `event_array`

- **Parameters**:
    - `NS_ROWS`: Number of rows in the 2D processing array.
        - Default value: 4.
        - Related interface signals: `i_en_overflow`, `i_event`, `i_bypass`.
    - `NS_COLS`: Number of columns in the 2D processing array.
        - Default value: 4. Must always be $`2^{NBW\_COL}`$
        - Related interface signals: `i_en_overflow`, `i_event`, `i_data`, `i_col_sel`.
    - `NBW_COL`: Bit width of the column selection signal.
        - Default value: 2.
        - Related interface signals: `i_col_sel`.
    - `NBW_STR`: Bit width of the data processed in each `event_storage`.
        - Default value: 8.
        - Related interface signals: `i_data`, `o_data`.
    - `NS_EVT`: Number of event bits handled by each `event_storage`.
        - Default value: 8. Must always be $`2^{NBW\_EVT}`$
        - Related interface signals: `i_event`.
    - `NBW_EVT`: Bit width of the read address used for event selection inside each `event_storage`.
        - Default value: 3.
        - Related interface signals: `i_raddr`.

### Interface Signals

- **Clock** (`clk`): Synchronizes operation at the rising edge.
- **Reset** (`rst_async_n`): Active-low asynchronous reset. Resets the internal storage elements.
- **Column Select** (`[NBW_COL-1:0] i_col_sel`): Selects which column’s output from the last row will be assigned to `o_data`.
- **Overflow Enable** (`[NS_ROWS*NS_COLS-1:0] i_en_overflow`): One-bit flag per `event_storage`. When high, enables overflow in `event_storage`'s internal registers.
- **Event Input** (`[(NS_ROWS*NS_COLS*NS_EVT)-1:0] i_event`): All events (flattened) to be applied across the array. Each `event_storage` receives `NS_EVT` bits.
- **Input Data** (`[(NS_COLS*NBW_STR)-1:0] i_data`): Parallel input data for the **first row only**, one value per column.
- **Bypass Control** (`[NS_ROWS-1:0] i_bypass`): One bit per row. When high, it bypasses the event logic in that row's `event_storage`.
- **Read Address** (`[NBW_EVT-1:0] i_raddr`): Address input used to read specific event-mapped data from each `event_storage`.
- **Output Data** (`[NBW_STR-1:0] o_data`): Output from the selected column in the **last row**.

### Functional Description

The `event_array` module is structured as a **2D pipeline** of `event_storage` units. Each unit represents a processing cell that performs bit-based updates to its internal data register according to the received `i_event` bits and the `i_en_overflow` flag.

The array is organized as `NS_ROWS` rows and `NS_COLS` columns.

#### Input Flow:
- Input data (`i_data`) is injected only into the **first row** of the array.
- Each subsequent row receives the processed output from the `event_storage` directly above it in the same column.
- All `event_storage` receive a unique slice of the flattened `i_event` and `i_en_overflow` arrays:
   - In `event_array`, the `i_event` input is a flat vector that holds all event bits for every cell in the grid, with each `event_storage` requiring `NS_EVT` bits. The module slices this vector by assigning `NS_EVT` bits to each `event_storage` based on its row and column. The slicing starts from the most significant bit and moves left to right across columns, then top to bottom across rows — like reading a table row by row. This way, each cell gets exactly the bits intended for its position in the array.
      - For example, if `NS_ROWS = 2`, `NS_COLS = 2`, and `NS_EVT = 4`, then `i_event` is 16 bits wide. The cell at row 0, column 0 gets the top 4 bits `[15:12]`, row 0, column 1 gets `[11:8]`, row 1, column 0 gets `[7:4]`, and row 1, column 1 gets the lowest 4 bits `[3:0]`.

   - The `i_en_overflow` input is a flat bit vector with one bit per `event_storage` in the grid. The vector is sliced using a row-major order: starting from the least significant bit, it maps left to right across columns, then top to bottom across rows.
      - For example, if `NS_ROWS = 2` and `NS_COLS = 2`, then `i_en_overflow` is 4 bits wide. The cell at row 0, column 0 gets bit `[0]`, row 0, column 1 gets bit `[1]`, row 1, column 0 gets bit `[2]`, and row 1, column 1 gets bit `[3]`.


#### Output Logic:
- After data has propagated through all rows, each column's final output is collected:
   - A `data_col_sel` signal is constructed by collecting the output data from each column in the last row of the array. For each column, the module takes the `data_out` of the `event_storage` cell at row `NS_ROWS - 1` and column `col`. These outputs are concatenated from **left to right** in **increasing column index order**, meaning **column 0 goes into the most significant bits**, and **column `NS_COLS - 1` goes into the least significant bits**. This signal is then connected to the input of the `column_selector` module.
      - For example, if `NS_COLS = 4` and `NBW_STR = 8`, then `data_col_sel` is 32 bits wide. The output from column 0 goes into bits `[31:24]`, column 1 into `[23:16]`, column 2 into `[15:8]`, and column 3 into `[7:0]`.

- The `column_selector` submodule then selects one column based on `i_col_sel` to produce the module's final output `o_data`.
