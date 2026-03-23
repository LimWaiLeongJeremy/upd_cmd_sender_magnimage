# Network
UDP_PORT: int = 41213
UDP_DUPLICATE_SEND_DELAY: float = 0.1  # seconds — hardware needs time between identical frames

# Brightness
BRIGHTNESS_MIN: int = 0
BRIGHTNESS_MAX: int = 100
BRIGHTNESS_BYTE_MAX: int = 255  # LED controller expects 0-255 internally

# Command frame structure
COMMAND_HEADER: list[int] = [0xED, 0xCB, 0x28, 0x38, 0x07, 0x01]
COMMAND_FOOTER_BYTE: int = 0x55
COMMAND_FOOTER_COUNT: int = 30
COMMAND_PADDING_BYTE: int = 0x00