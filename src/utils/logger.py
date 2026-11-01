
import logging
from pathlib import Path


def get_logger(name: str) -> logging.Logger:

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Write logs to a file
    file_handler = logging.FileHandler(
        log_dir / "pipeline.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Display logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
