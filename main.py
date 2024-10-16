"""This module contains the function's business logic.

Use the automation_context module to wrap your function in an Automate context helper.
"""

from speckle_automate import (
    execute_automate_function,
)

from src.logic import automate_function, automate_function_without_inputs

# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference; do not invoke it!

    # Pass in the function reference with the inputs schema to the executor.
    # execute_automate_function(automate_function, FunctionInputs)

    # If the function has no arguments, the executor can handle it like so
    execute_automate_function(automate_function_without_inputs)
