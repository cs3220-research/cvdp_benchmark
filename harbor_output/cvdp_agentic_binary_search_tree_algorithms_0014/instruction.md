You are provided with three SystemVerilog modules in the rtl/ directory. You need to integrate these three modules into a top-level module called `bst_operations`,  which should support the operations described further in the specification in the docs/bst_operations.md. 

1. `search_binary_search_tree` — performs key search in a binary search tree (BST)  
2. `delete_node_binary_search_tree` — deletes a node with the given key from the BST  
3. `binary_search_tree_sort_construct` — performs both BST construction and  sorting  via in-order traversal 

---

### Required Modifications

1. The module `binary_search_tree_sort_construct` currently combines **BST construction** and **sorting** into one module.  
   Create **two separate functional modules** using `binary_search_tree_sort_construct` as the reference to be able to provide a BST input to the `search_binary_search_tree` and `delete_node_binary_search_tree` modules and optionally sort after the operations. While creating modules for separating the operations, add necessary input/output ports to the new submodules to propagate data between modules. (Only top module consistency needs to be retained as per the spec).
   - `bst_tree_construct`: builds the BST
   - `binary_search_tree_sort`: performs in-order traversal to output sorted keys

2. You must **connect these new modules** inside `bst_operations` along with  `search_binary_search_tree` and  `delete_node_binary_search_tree`

3. No additional latency other than that for handling completion flags must be added in between operations. 

---

### Key Handling Consistency

There is an inconsistency in how **invalid keys** are handled across the modules. The original `binary_search_tree_sort_construct`  module uses `0` to indicate **invalid keys**. In contrast, both `search_binary_search_tree` and `delete_node_binary_search_tree` use **all 1s** (`{DATA_WIDTH{1'b1}}`) to represent invalid key values

- Ensure that all modules within `bst_operations` use **consistent invalid key and pointer representations**  
- Recommended:
  - `INVALID Key = {DATA_WIDTH{1'b1}}`
  - `INVALID Pointer = {($clog2(ARRAY_SIZE)+1){1'b1}}`

---

###  Top-Level Interface

The `bst_operations` module must:
- Accept input data as a flattened array (`data_in`)
- Accept a key (`operation_key`) and operation selector (`operation`)
- Output the updated BST structure and, optionally, sorted keys
- Output flags to indicate operation completion and validity
---
