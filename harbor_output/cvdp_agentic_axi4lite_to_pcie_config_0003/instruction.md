Modify `axi4lite_to_pcie_cfg_bridge` module with read functionality, which is a critical part of any `AXI4-Lite` interface. In an `AXI4-Lite-based` system, both write and read transactions are required to allow the CPU or other `master` devices to communicate with peripherals and memory-mapped registers effectively. Refer to the specification provided in docs/axilite_to_pcie_config_module.md to implement the RTL for Read transaction.

## Modifications to the RTL for Read Support :
#### To support read transactions, we need to introduce:
- New Read-Related Ports in the module interface.
- FSM Modifications to handle read transactions.
- Additional Internal Logic to drive the read response.
---
### Proposed Modifications 

This module is parameterized, allowing flexibility in configuring **data width, address width**.

- **`DATA_WIDTH`**: Configures the bit-width of data. Default value is **32 bits**.
- **`ADDR_WIDTH`**: Determines the config memory size by specifying the number of address bits. Default value is **8 bits**.
 
#### Here is a table describing the ports to be added newly for handling read transactions:

#### **IO Ports Description**
| Port Name | Direction | Width   | Description                        |
|-----------|-----------|---------|------------------------------------|
| araddr    | Input     | 8-bits  | Read address from AXI4-Lite master |
| arvalid   | Input     | 1-bit   | Read address valid signal          |
| arready   | Output    | 1-bit   | Read address ready signal          |
| rdata     | Output    | 32-bits | Read data output                   |
| rvalid    | Output    | 1-bit   | Read data valid signal             |
| rready    | Input     | 1-bit   | Read data ready signal             |
| rresp     | Output    | 2-bit   | Read response signal               |

**Read FSM Implementation**

The read transaction follows a similar FSM pattern as the write transaction but includes the following states:
- `IDLE` – Waits for `arvalid` to be asserted.
- `ADDR_CAPTURE` – Captures the read address.
- `PCIE_READ` – Initiates a read operation from PCIe configuration space.
- `SEND_RESPONSE` – Sends the read data back to the AXI4-Lite master.

These states ensure that the read request is handled efficiently while maintaining AXI4-Lite protocol compliance.

---

### **Module Specification: `axi4lite_to_pcie_cfg_bridge`**

This section specifies the current version of the module before modification. The axi4lite_to_pcie_cfg_bridge module implements AXI4Lite write functionality.

The AXI4-Lite to PCIe Configuration Space Bridge provides an interface for writing configuration data to the PCIe Configuration Space using the AXI4-Lite protocol. This ensures seamless communication between the AXI4-Lite master and PCIe configuration registers. The bridge translates AXI4-Lite transactions into PCIe-compatible signals, enabling system configurations and status updates through register writes.

Write Port Descriptions:
|    Port Name   | Direction |  Width  |                  Description                  |
|:--------------:|:---------:|:-------:|:---------------------------------------------:|
| awaddr         | Input     | 8-bits  | Write address from AXI4-Lite master.          |
| awvalid        | Input     | 1-bit   | Write address valid signal.                   |
| awready        | Output    | 1-bit   | Write address ready signal.                   |
| wdata          | Input     | 32-bits | Write data from AXI4-Lite master.             |
| wstrb          | Input     | 4-bits  | Write strobe signal to indicate active bytes. |
| wvalid         | Input     | 1-bit   | Write data valid signal.                      |
| wready         | Output    | 1-bit   | Write data ready signal.                      |
| bresp          | Output    | 2-bit   | Write response (OKAY, SLVERR, etc.).          |
| bvalid         | Output    | 1-bit   | Write response valid signal.                  |
| bready         | Input     | 1-bit   | Write response ready signal.                  |
| pcie_cfg_addr  | Output    | 8-bits  | PCIe configuration address for transaction.   |
| pcie_cfg_wdata | Output    | 32-bits | Data to be written into PCIe config space.    |
| pcie_cfg_wr_en | Output    | 1-bit   | Write enable for PCIe configuration space.    |
| pcie_cfg_rdata | Input     | 32-bits | Data read from PCIe configuration space.      |
| pcie_cfg_rd_en | Input     | 1-bit   | Read enable for PCIe configuration space.     |

---

### Write Transaction Flow
The write process consists of the following steps:
**Address Phase:**
- The AXI4-Lite master sends the write address (`awaddr`) along with `awvalid`.
- The bridge asserts `awready` when it is ready to accept the address.

**Data Phase:**
- The master provides the write data (`wdata`) and write strobes (`wstrb`).
- The bridge asserts `wready` to indicate it is ready to accept the data.

**PCIe Write Transaction:**
- The bridge forwards the write address (`pcie_cfg_addr`) and data (`pcie_cfg_wdata`) to the PCIe Configuration Space.
- `pcie_cfg_wr_en` is asserted to signal a valid PCIe write operation.

**Write Response:**
- Once the write is complete, the bridge asserts `bvalid` with an acknowledgment response (`bresp`).
- The master acknowledges by asserting `bready`, completing the transaction.

**Write Process Example**
***Input***
|  Signal |     Value    |            Description           |
|:-------:|:------------:|:--------------------------------:|
| awaddr  | 32'h00000010 | Address to write data to.        |
| awvalid | 1'b1         | Address is valid.                |
| wdata   | 32'hAABBCCDD | Data to be written.              |
| wstrb   | 4'b1111      | Writing all 4 bytes.             |
| wvalid  | 1'b1         | Write data is valid.             |
| bready  | 1'b1         | Ready to receive write response. |

***Output***
|     Signal     |     Value    |          Description          |
|:--------------:|:------------:|:-----------------------------:|
| awready        | 1'b1         | Write address is accepted.    |
| wready         | 1'b1         | Write data is accepted.       |
| pcie_cfg_addr  | 8'h10        | PCIe address for transaction. |
| pcie_cfg_wdata | 32'hAABBCCDD | Data to be written to PCIe.   |
| pcie_cfg_wr_en | 1'b1         | PCIe write enable asserted.   |
| bvalid         | 1'b1         | Write response is valid.      |
| bresp          | 2'b00 (OKAY) | Write successful response.    |

The code should be well-documented with clear comments explaining the functionality of each major block. Follow best practices in SystemVerilog coding to ensure readability, reusability, and maintainability.
