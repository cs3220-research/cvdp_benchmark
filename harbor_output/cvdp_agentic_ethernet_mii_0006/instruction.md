Implement an Ethernet MAC TX subsystem in `rtl/ethernet_mac_tx.sv`, integrating with a dual-port memory (DP-RAM) module for frame data buffering, as specified in `docs/tx_mac_specification.md`.

**Step 1:**  
- Implement the Dual-Port RAM module in `rtl/ethernet_dp_ram.sv` with:
  - Single-clock operation using `clk_in`
  - Two access ports:
    - **Port 0 (Configuration Port):**
      - Inputs: `addr0_in` (word-aligned address), `data0_in`, and `wr0_in`
      - Output: `data0_out` (data available after one clock cycle delay)
    - **Port 1 (Transmit Port):**
      - Input: `addr1_in` for sequential reading
      - Output: `data1_out` (data available with one clock cycle read latency)
      
**Step 2:**  
- Implement the Ethernet MAC TX subsystem in `rtl/ethernet_mac_tx.sv` with DP-RAM integration, including:
  -  Configuration Interface.
  - **Operational Modes:**
    - **Normal Mode:** Program complete frame data (MAC addresses and payload) before triggering transmission
    - **MAC Program Mode:** Update only the MAC addresses and reuse previously programmed payload data by asserting the PROGRAM bit with the BUSY indicator
  - **AXI-Stream Interface:**
    - Generate outputs: `axis_tdata_out` (32-bit), `axis_tstrb_out` (4-bit), `axis_tvalid_out`, and `axis_tlast_out`
    - Respect the `axis_tready_in` signal for flow control
  - **Interrupt Generation:**
    - Generate an interrupt upon complete frame transmission if enabled via register 0x07F8
