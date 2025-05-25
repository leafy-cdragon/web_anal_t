# custom_exceptions.py

class WebAnalysisToolException(Exception):
    """Base exception class for the Web Analysis Tool."""
    pass

class DataCollectionError(WebAnalysisToolException):
    """Exception raised for errors in the data collection process."""
    pass

class BackendAnalysisError(WebAnalysisToolException):
    """Exception raised for errors in the backend analysis process."""
    pass

class PGPManagementError(WebAnalysisToolException):
    """Exception raised for errors in PGP key management or operations."""
    pass

class GUIError(WebAnalysisToolException):
    """Exception raised for errors related to the GUI operations."""
    pass

class ConfigurationError(WebAnalysisToolException):
    """Exception raised for configuration-related errors."""
    pass

