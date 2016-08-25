meta:
  id: TASCAM_blackfin_firmware
  endian: be
seq:
  - id: device_name
    type: str
    size: 8
    encoding: ASCII
  - id: fw_version
    type: u2
  - id: numeric_version
    type: u2
  - id: year
    type: u2
  - id: day
    type: u1
  - id: month
    type: u1
  - id: checksum
    type: u4
    size: 4
  - id: fw_file_size
    type: u4

