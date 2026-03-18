from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import time
import argparse
from tqdm import tqdm
from logging import setup_logger
from command_former import form_command
import utils.logger

def get_target_ips(groups):
    """Get the list of target IPs based on the specified groups."""
    target_ips = []
    for group in groups:
        target_ips.extend(utils.logger.main.get(group, []))
        target_ips.extend(utils.logger.backup.get(group, []))
    return target_ips


def send_command(ip, command):
    """Send a UDP command to the specified IP address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(command, (str(ip), 41213))  # Assuming port 41213 for the command
        time.sleep(0.1)  # Short delay to ensure the command is sent
        sock.sendto(command, (str(ip), 41213))  # Assuming port 41213 for the command
    finally:
        sock.close()


def send_brightness_commands(ip, start_brightness_persentage, end_brightness_persentage, duration, step, logger):
    
    """Send brightness commands from start_brightness to end_brightness."""
        # Determine direction and adjust end value accordingly
    
    if start_brightness_persentage <= end_brightness_persentage:
        # Going upward
        end_value = end_brightness_persentage + 1
    else:
        # Going downward
        end_value = end_brightness_persentage - 1
        
    for brightness in tqdm(range(start_brightness_persentage, end_value, int(step)), desc=f"Sending Commands to {ip}"):
        command = form_command(brightness)
        send_command(ip, command)
        logger.info(f"Sent command to {ip} with brightness {brightness}%")
        time.sleep(duration)

def main():

    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(description="Send UDP brightness commands to specified groups.")
    parser.add_argument("start_brightness_persentage", type=int, help="Start brightness level (0-100)")
    parser.add_argument("end_brightness_persentage", type=int, help="End brightness level (0-100)")
    parser.add_argument("step", type=int, help="Step size for brightness changes")
    parser.add_argument("duration", type=float, help="Duration to wait between commands (seconds)")
    parser.add_argument("--groups", nargs="+", default=["m", "ac", "b", "e", "ctrl"], help="Groups to send commands to (default: all groups)")
    args = parser.parse_args()
    logger = setup_logger("brightness_commands.log")

    # Validate the brightness levels
    if args.start_brightness_persentage < 0 or args.start_brightness_persentage > 100 or args.end_brightness_persentage < 0 or args.end_brightness_persentage > 100:
        logger.error(f"Brightness levels must be between 0 and 100, user keyed in {args.start_brightness_persentage} to {args.end_brightness_persentage}.")
        print("Brightness levels must be between 0 and 100")
        exit(1)

    # Validate the duration
    if args.duration <= 0:
        logger.error(f"Duration must be a positive number, user keyed in {args.duration}.")
        print("Duration must be a positive number.")
        exit(1)

    #  Get the main and backup IP lists based on the specified groups
    all_ips = get_target_ips(args.groups)

    with ThreadPoolExecutor() as executor:
        # build one future per address
        futures = [
            executor.submit(
                send_brightness_commands,
                ip,
                args.start_brightness_persentage,
                args.end_brightness_persentage,
                args.duration,
                args.step,
                logger
            )
            for ip in all_ips
        ]

        # wait for them all; tqdm can show progress
        for future in as_completed(futures):
            # re‑raise any exceptions that happened in the worker
            future.result()
        print ("All commands sent successfully.")

if __name__ == "__main__":
    main()