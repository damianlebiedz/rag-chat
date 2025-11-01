class MissingOrInvalidEnvironmentVariableError(Exception):
    """Raised when an environment variable is missing or invalid."""
    def __init__(self, var_names):
        if isinstance(var_names, str):
            var_names = [var_names]
        super().__init__(f"Missing or invalid environment variable(s): {', '.join(var_names)}")
        self.var_names = var_names
