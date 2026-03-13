def form_command(brightness):
    """Form the command with the given brightness value."""
    
    brightness_persent_in_hex = convert_brightness_to_hex(brightness)
    # Define the command structure
    command = [0xED, 0xCB, 0x28, 0x38, 0x07, 0x01, brightness_persent_in_hex, 0x00] + [0x55] * 30
    # # Calculate the checksum
    checksum = calculate_checksum(command)
    # # Append the checksum to the command
    command.append(checksum)
    return bytes(command)


def calculate_checksum(command):
    """Calculate the checksum for the command."""
    checksum = sum(command) & 0xFF  # Sum all bytes and take the last 8 bits
    return checksum

def convert_brightness_to_hex(brightness):
    """Convert brightness level to hexadecimal."""
    decimal_value = int(brightness * 255 / 100)
    
    return max(0, min(255, decimal_value))