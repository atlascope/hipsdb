import logging
import sys
import blessings


def initialize_logging() -> tuple[logging.Logger, logging.Formatter]:
    term = blessings.Terminal()

    class HipsFormatter(logging.Formatter):
        Colors = {
            logging.DEBUG: term.green,
            logging.INFO: term.blue,
            logging.WARNING: term.yellow,
            logging.ERROR: term.red,
            logging.CRITICAL: term.bold_red,
        }

        def __init__(self, *args, **kwargs):
            self.spacing = 0
            self.supports_color = sys.stdout.isatty() and sys.stderr.isatty()
            super().__init__(*args, **kwargs)

        def format(self, record):
            record.levelname = record.levelname.ljust(len("CRITICAL"))
            record.msg = " " * self.spacing + record.msg
            color = self.__class__.Colors.get(record.levelno, term.normal)
            if self.supports_color:
                record.msg = color(record.msg)
            return super().format(record)

        def indent(self):
            self.spacing += 2

        def dedent(self):
            self.spacing -= 2
            if self.spacing < 0:
                self.spacing = 0

    logger = logging.getLogger(__name__)
    formatter = HipsFormatter("[%(name)s/%(levelname)s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger, formatter
