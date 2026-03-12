I have a **sorting_engine** module that sorts the input data in ascending order.

The **sorting_engine** module is available at `/rtl/sorting_engine.sv` and its' specification in the `/docs` directory.
Can you implement the **`order_matching_engine.sv`** in the `/rtl` folder? Details of the `order_matching_engine` module is as given below

**Description - Order Matching Engine**

The goal is to build a module that efficiently processes and matches buy (bid) and sell (ask) orders. Here’s what the design must accomplish:

- **Input Handling:**  
  The engine accepts two flat input vectors—one for bid orders and one for ask orders. Each vector contains 8 orders (prices) of configurable bit-width (`PRICE_WIDTH`).

- **Sorting:**  
  Use the provided sorting engine to sort each set of orders:
  - Bid orders are sorted in ascending order (so the highest bid is at the last position).
  - Ask orders are sorted in ascending order (so the lowest ask is at the first position).

- **Order Matching:**  
  After sorting, extract the best bid (highest bid) and best ask (lowest ask). If the best bid is greater than or equal to the best ask, a match occurs. The matching price is taken as the best ask.

- **Latency Requirement:**  
  The design must contain logic to measure and ensure that the total processing latency, from the issuance of a start signal to the output being valid, is exactly 21 clock cycles.

- **Port List:**
```verilog
   module order_matching_engine #(
    parameter PRICE_WIDTH = 16  // width of the price field
)(
    input                      clk,
    input                      rst,
    input                      start,         // start matching operation
    input  [8*PRICE_WIDTH-1:0] bid_orders,    // 8 bid orders (flat vector)
    input  [8*PRICE_WIDTH-1:0] ask_orders,    // 8 ask orders (flat vector)
    output reg                 match_valid,   // high if a match occurs
    output reg [PRICE_WIDTH-1:0] matched_price, // matched price (best ask)
    output reg                 done,          // matching engine done
    output reg                 latency_error  // asserted if latency ≠ 20 cycles
);
```
