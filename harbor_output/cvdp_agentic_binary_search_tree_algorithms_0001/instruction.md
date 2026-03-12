I have a module `search_binary_search_tree` in the `rtl` directory that performs a search for a given `search_key` in a binary search tree (BST) which is given as an array of unsigned integers with a parameterizable size, `ARRAY_SIZE` (greater than 0). The module locates the position of the `search_key` in the array sorted with the constructed BST. The position where the `search_key` is located is based on its **position in the sorted array** (sorted such that the smallest element is at index 0 and the largest element is at index `ARRAY_SIZE`-1). Modify the existing SystemVerilog code to a module named `delete_node_binary_search_tree` to correctly implement the deletion of a node in the given BST input after its searching is completed. The renamed module should be in the same file `rtl/search_binary_search_tree.sv`. The specification of the new module is available in `docs` directory.
The module should handle the following scenarios:

1. When the node to search and delete has both left and right children.
2. When the node to search and delete has only a left child.
3. When the node to search and delete has only the right child.
4. When the node to search and delete has no children.

The module should also ensure that the BST structure is maintained after deletion, and invalid keys and pointers are correctly updated. The interfaces for the modified code must remain similar to that of the existing code with some additional interfaces relevant to the deletion logic. The `search_key`, `complete_found`and `search_invalid` input in the `search_binary_search_tree` module must be replaced with `delete_key`, `complete_deletion` and `delete_invalid` to adapt better to the deletion operation. Additional outputs relevant to the deletion logic must include modified BST consisting of key, left_child, and right_child with the `delete_key` deleted, and invalid keys and pointers correctly updated.

The latency for the total deletion for the modified code depends on the depth of the tree to search the node. In the worst case, the FSM will traverse the depth of the tree. The latency of the search algorithm must be maintained similar to the existing algorithm. 

---

### Task

1. **Review the Existing Code:**
   - Ensure the FSM correctly transitions between states.
   - Verify that the search logic correctly identifies the node to delete.
   - The search logic determines the index of the node to be deleted and information about its left and right child.

2. **Implement the Deletion Logic:**
   - Handle all deletion scenarios in the `S_DELETE` state.
   - Ensure that the BST structure is maintained after deletion.
   - Update the `modified_keys`, `modified_left_child`, and `modified_right_child` arrays correctly.

3. **Handle Invalid Keys and Pointers:**
   - Replace deleted keys and pointers with the appropriate invalid values.
   - Ensure that any references to the deleted node are updated to point to invalid values.

4. **Handle Reset of Outputs and Control Flags:**
   - After the deletion is complete for a given input BST and `delete_key`, ensure the output and control flags are reset to their reset value.

---

### Example Test Cases for DATA_WIDTH = 6
1. **Delete Node with Both Children:**
   - Input: `keys = [10, 5, 15, 3, 7, 12, 20]`, `left_child = [1, 3, 5, 15, 15, 15, 15]`, `right_child = [2, 4, 6, 15, 15, 15, 15]`, `delete_key = 10`
   - Expected Output: `modified_keys = [12, 5, 15, 3, 7, 63, 20]`, `modified_left_child = [1, 3, 15, 15, 15, 15, 15]`, `modified_right_child = [2, 4, 6, 15, 15, 15, 15]`

2. **Delete Node with Only Left Child:**
   - Input: `keys = [10, 5, 15, 3, 63, 12, 20]`, `left_child = [1, 3, 5, 15, 15, 15, 15]`, `right_child = [2, 4, 6, 15, 15, 15, 15]`, `delete_key = 5`
   - Expected Output: `modified_keys = [10, 3, 15, 63, 63, 12, 20]`, `modified_left_child = [1, 15, 5, 15, 15, 15, 15]`, `modified_right_child = [2, 4, 6, 15, 15, 15, 15]`

3. **Delete Node with No Children:**
   - Input: `keys = [10, 5, 15, 3, 7, 12, 20]`, `left_child = [1, 3, 5, 15, 15, 15, 15]`, `right_child = [2, 4, 6, 15, 15, 15, 15]`, `delete_key = 3`
   - Expected Output: `modified_keys = [10, 5, 15, 63, 7, 12, 20]`, `modified_left_child = [1, 15, 5, 15, 15, 15, 15]`, `modified_right_child = [2, 4, 6, 15, 15, 15, 15]`

---

### Deliverables
Ensure that the modified SystemVerilog code correctly implements the deletion logic for all scenarios and maintains the BST structure.
