import logging

from slugline_mcp.config import load_config
from slugline_mcp.server import mcp


def main():
    config = load_config()
    logging.basicConfig(level=config.log_level)
    mcp.run()


if __name__ == "__main__":
    main()
