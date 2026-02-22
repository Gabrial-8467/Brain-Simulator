import logging
import os


class BrainLogger:
    def __init__(self, config: dict = None):
        config = config or {}

        level = config.get("level", "INFO").upper()
        self.logger = logging.getLogger("VirtualBrain")

        if not self.logger.handlers:
            self.logger.setLevel(getattr(logging, level, logging.INFO))

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            if config.get("log_to_file", False):
                file_path = config.get("file_path", "logs/brain.log")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                file_handler = logging.FileHandler(file_path)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
