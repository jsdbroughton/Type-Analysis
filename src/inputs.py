from pydantic import Field
from speckle_automate import AutomateBase


class FunctionInputs(AutomateBase):
    """These are function author-defined values.

    Automate will make sure to supply them matching the types specified here.
    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """

    # An example of how to use secret values.
    percentage_mean_cutoff: float = Field(
        title="Percentage of Mean cutoff",
        description=(
            "Any type with a frequency less than this percentage of the mean"
            " it will be marked as a special type."
        ),
    )
