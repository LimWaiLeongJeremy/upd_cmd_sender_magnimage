import logging
import socket
import time

from constants import UDP_PORT, UDP_DUPLICATE_SEND_DELAY

logger = logging.getLogger(__name__)

def send_udp_packets(
    ip: str, 
    payload: bytes, 
    port: int = UDP_PORT, 
    duplicate: bool = True
) -> None:
    """
    Send a UDP payload to the target host.

    The `duplicate` flag controls whether the packet is sent twice.
    The FW16-C controller benefits from duplicate sends to compensate
    for potential packet loss on the local network segment.

    Args:
        ip:        Target IP address as a string.
        payload:   Raw bytes to transmit.
        port:      UDP destination port (default: constants.UDP_PORT).
        duplicate: If True, send the payload a second time after a short delay.
    """ 
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(payload, (ip, port))
        logger.debug(f"UDP packet sent → {ip}:{port} ({len(payload)} bytes)")
        
        if duplicate:
            time.sleep(UDP_DUPLICATE_SEND_DELAY)
            sock.sendto(payload, (ip, port))
            logger.debug(f"UDP duplicate sent → {ip}:{port}")
    except OSError as exc:
        logger.error(f"Network error sending to {ip}:{port} — {exc}")
        raise
        
    