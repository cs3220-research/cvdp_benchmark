### `slicer_top` (`slicer_top.sv`)

The **slicer_top** module must be updated with the following changes:

- Introduce a new parameter: **`NBW_OUT`**, which configures the bit width of the output signal of `slicer` module.
- **Remove** the parameter **`NS_TH`**.
- Replace the current threshold interface. The input signal **`i_threshold`** must now be a single **packed signal** with a bit width of **`NBW_TH`**.
- **Remove** the following input signals:
  - `i_sample_0_pos`
  - `i_sample_0_neg`
  - `i_sample_1_neg`
- **Rename** the signal `i_sample_1_pos` to `i_sample_pos`.

#### Parameter Constraint

The parameter **`NBW_OUT`** must be large enough to represent the result of adding two signed values (this ensures proper bit width to handle the signed addition without overflow):
- One using **`NBW_TH`** bits
- One using **`NBW_REF`** bits

---

### `slicer` (`slicer.sv`)

At the module level of **`slicer`**, the **same interface and parameter changes** applied to `slicer_top` must be mirrored:

- Add the **`NBW_OUT`** parameter.
- Remove the **`NS_TH`** parameter.
- Update the input **`i_threshold`** to be a single **packed signal** with bit width **`NBW_TH`**.
- Remove the following signals:
  - `i_sample_0_pos`
  - `i_sample_0_neg`
  - `i_sample_1_neg`
- Rename `i_sample_1_pos` to `i_sample_pos`.

---

### Comparison and Processing Logic

In the **`slicer`** module, all comparisons must rely solely on the updated **`i_threshold`** signal.

- When comparing the input to thresholds, use **`i_threshold`** and its **negated value** to define the positive and negative limits.
- The output signal **`o_data`** must receive a result based on **accumulated sums** of `i_sample_pos` and `i_threshold`, where the **sign of the sample** depends on whether the input value is above or below the defined thresholds.
- Internally, use the unified `i_sample_pos` signal and apply the appropriate **sign (positive or negative)** based on input value comparisons with the threshold.
