"""
All logic related to building the UDP command frame for the
Magnimage FW16-C LED Video Controller.

Frame structure (39 bytes total):
  [0]    0xED  — Header byte 1
  [1]    0xCB  — Header byte 2
  [2]    0x28  — Header byte 3
  [3]    0x38  — Header byte 4
  [4]    0x07  — Header byte 5
  [5]    0x01  — Header byte 6
  [6]    BVAL  — Brightness value (0x00–0xFF)
  [7]    0x00  — Padding
  [8-37] 0x55  — 30 footer bytes
  [38]   CSUM  — Checksum (sum of bytes 0–37, lower 8 bits)
"""