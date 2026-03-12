Design a `pcie_endpoint` module in System Verilog which is responsible for handling `PCIe transactions`, interfacing with a `DMA engine`, and managing `MSI-X interrupts`. It processes `PCIe Transaction Layer Packets` (TLPs), decodes them, and executes the corresponding read/write operations. This module follows a `Finite State Machine` (FSM) approach to ensure proper sequencing of PCIe endpoint write and read transactions. The design is parameterizable, allowing flexibility in configuring data width and address width. Please refer to the specification provided in `docs/specs.md` for detailed design description.

## **Parameterization**
- **Address Width (`ADDR_WIDTH`)**: Default **64 bits**, configurable for different PCIe address sizes.
- **Data Width (`DATA_WIDTH`)**: Default **128 bits**, supporting high-speed PCIe transfers.

## **1. Features**
### **PCIe Transaction Handling**
- Receives PCIe TLPs and processes valid transactions.
- Decodes received TLPs and forwards them for execution.
- Transmits processed transactions.

### **DMA Engine Interface**
- Supports DMA requests and generates corresponding complete requests.
- Provides `dma_address` and `dma_data` signals to interact with external memory controllers.

### **MSI-X Interrupt Management**
- Generates MSI-X interrupts upon DMA completion.
- Ensures proper sequencing of interrupt generation to prevent missed events.

## **2. Functional Description**
The `pcie_endpoint` module consists of multiple FSMs, each handling a distinct function:

### **PCIe Transaction FSM**
- Manages the reception and processing of incoming PCIe TLPs.
- Decodes received transactions and prepares them for further execution.

### **PCIe Data Link FSM**
- Handles transmission of PCIe transactions.
- Ensures data integrity and proper sequencing of outgoing TLPs.

### **DMA FSM**
- Manages the interaction with the DMA engine.
- Tracks DMA requests and ensures completion of memory operations.

### **MSI-X FSM**
- Generates MSI-X interrupts upon successful completion of DMA operations.
- Ensures correct signaling of interrupts to the host system.

## **3. Transaction Flow**
### **PCIe Write Transaction**
1. Receives a PCIe TLP.
2. Decodes and processes the transaction.
3. Stores the data in the appropriate memory location.

### **PCIe Read Transaction**
1. Receives a read request from PCIe.
2. Fetches the required data from memory.
3. Sends the data as a PCIe response.

### **DMA Transaction**
1. Receives a DMA request.
2. Reads or writes data from/to memory.
3. Signals DMA completion.

### **MSI-X Interrupt Generation**
1. Detects completion of DMA operations.
2. Generates an MSI-X interrupt signal.
3. Waits for acknowledgment before resetting the interrupt state.

## **4. SystemVerilog Best Practices**
- **Modular Design:** FSMs are independently implemented for different functions, ensuring better maintainability.
- **Parameterization:** Address and data width are configurable to accommodate various PCIe configurations.
- **Clock Domain Handling:** All FSMs operate under a single `clk` domain to maintain synchronization.
- **Reset Handling:** The `rst_n` signal ensures proper initialization of all FSMs and state registers.

The code follows best practices in SystemVerilog, ensuring readability, reusability, and maintainability. Proper comments and documentation are included to explain the functionality of each major block.
