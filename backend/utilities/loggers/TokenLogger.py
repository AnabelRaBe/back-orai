"""
TokenLogger
"""
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from ..helpers.EnvHelper import EnvHelper

class TokenLogger:
    """
    Class for logging tokens.
    """
    def __init__(self, name: str = __name__):
        """
        Initialize the TokenLogger.
        Parameters:
            name (str, optional): The name of the logger. Defaults to __name__.
        """
        env_helper : EnvHelper = EnvHelper()
        self.logger = logging.getLogger(name)
        self.logger.addHandler(AzureLogHandler(connection_string=env_helper.APPINSIGHTS_CONNECTION_STRING))
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        """
        Get the logger instance.
        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger

    def log(self, message: str, custom_dimensions: dict):
        """
        Log a message with custom dimensions.
        Parameters:
            message (str): The message to log.
            custom_dimensions (dict): Custom dimensions for the log message.
        """
        # Setting log properties
        log_properties = {
            "custom_dimensions": custom_dimensions
        }
        self.logger.info(message, extra=log_properties)
