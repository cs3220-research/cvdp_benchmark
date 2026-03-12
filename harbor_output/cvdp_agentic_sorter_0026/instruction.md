I have a few **sorting_engine** modules that sort the input data in ascending order. The **sorting_engine** modules are available at `rtl/` directory. Each module present in the folder implements a different sorting algorithm to perform the sorting operation. The sorting algorithm used by a module is mentioned in the name of the module.

Can you implement the **`order_matching_engine.sv`** in the `rtl` folder? Details of the `order_matching_engine` module are as given below

**Description - Order Matching Engine**

The goal is to build a module that efficiently processes and matches buy (bid) and sell (ask) orders. Here’s what the design must accomplish:

- **Input Handling:**  
  The engine accepts two flat input vectors—one for bid orders and one for ask orders. Following are the bid and ask order vectors:
Bid: 42,74,10,21,108,53,95,106
Ask: 130,108,205,129,192,213,244,141

- **Sorting:**  
  Select the sorting_engine module that has the lowest latency for the provided input to sort each set of orders. Use the same sorting algorithm implementation for sorting both bid and ask orders.
  - Bid orders are sorted in ascending order (so the highest bid is at the last position).
  - Ask orders are sorted in ascending order (so the lowest ask is at the first position).

- **Order Matching:**  
  After sorting, extract the best bid (highest bid) and best ask (lowest ask). If the best bid is greater than or equal to the best ask, a match occurs. The matching price is taken as the best bid.

- **Safeguarding:**
   The design should have a safeguard to cap the total loss in the event this module is used for trading purpose. Use the input circuit breaker that should disable any successful matches irrespective of the incoming bid and ask orders.

- **Latency:**
   The order_matching_engine that is generated should add a latency of exactly 1 clock cycle on top of the latency of the sorting_engine module it uses.

- **Port List:**
```verilog
   module order_matching_engine #(
    parameter PRICE_WIDTH = 16  // width of the price field
)(
    input                      clk,
    input                      rst,
    input                      start,         // Active high. Start matching operation
    input                      circuit_breaker, //Active high. Circuit breaker
    input  [8*PRICE_WIDTH-1:0] bid_orders,    // 8 bid orders (flat vector)
    input  [8*PRICE_WIDTH-1:0] ask_orders,    // 8 ask orders (flat vector)
    output reg                 match_valid,   // High if a match occurs
    output reg [PRICE_WIDTH-1:0] matched_price, // Matched price (best bid)
    output reg                 done          // Active high. Matching engine done
);
```
