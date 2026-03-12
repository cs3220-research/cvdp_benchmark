I need to implement a **64b/66b top-level codec module** that integrates a **data encoder (`encoder_data_64b66b`), a control encoder (`encoder_control_64b66b`), and a combined data/control decoder (`decoder_data_control_64b66b`)**. The top-level module should be created at **`/code/rtl/top_64b66b_codec.sv`** and must manage the full encode-decode flow for 64b/66b encoding, supporting data, and control paths.

The encoder must select between data and control encoding based on the `enc_control_in` value and produce a 66-bit encoded output (`enc_data_out`). The decoder must process incoming 66-bit data and output 64-bit decoded data, associated control signals, and any sync or decoding errors.

The RTL source files are located as follows:
- `/code/rtl/encoder_data_64b66b.sv`
- `/code/rtl/encoder_control_64b66b.sv`
- `/code/rtl/decoder_data_control_64b66b.sv`

The documentation, located under the`/code/docs/specification.md` directory, provides design requirements and behavior specifications. 

This integrated module should operate with **minimal latency and full protocol compliance**, as defined in the provided documentation.
