import logging

def setup_logger(
    name: str,
    log_file: str | None = None,
    level: int = logging.INFO,
    to_console: bool = True,
) -> logging.Logger:
    """
    Create (or retrieve) a named logger with file and/or console output.

    Calling this multiple times with the same name is safe — handlers are
    only added once. This prevents "duplicate log lines" bug.

    Args:
        name:        Logger name. Use __name__ in each module.
        log_file:    Path to log file. None = no file output.
        level:       Logging level (default: INFO).
        to_console:  Whether to also log to stdout.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    # Guard: don't add handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
