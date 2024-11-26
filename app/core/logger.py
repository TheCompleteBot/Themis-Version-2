import logging
import sys
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a custom logger
logger = logging.getLogger("themis_logger")
logger.setLevel(logging.INFO)

# Define handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler('logs/themis.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)
