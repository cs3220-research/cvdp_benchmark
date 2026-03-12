I have a `sorting_engine` module available in the `rtl` directory and its' specification in the `docs` directory. The existing sorting_engine module implements the sorting of an unsigned integer array using a parallel merge sort algorithm in 20 clock cycles.

Modify the code to reduce the latency to 17 clock cycles by merging FSM states that can be executed in parallel.

Make sure to follow the given constraints:
- The reset behavior and constraints of the existing `sorting_engine` module should still be valid.
- Retain the original module (`sorting_engine`) port list interface.
- Retain the behavior where sorting arranges the elements of the array in ascending order, such that the smallest element is at index 0 and the largest element is at index N−1.
