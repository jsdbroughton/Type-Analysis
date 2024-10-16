from speckle_automate import (
    AutomationContext,
    AutomationRunData,
    AutomationStatus,
    run_function
)
from speckle_automate.fixtures import *

from src.inputs import FunctionInputs
from src.logic import automate_function


def test_function_run(test_automation_run_data: AutomationRunData, test_automation_token: str):
    automation_context = AutomationContext.initialize(
        test_automation_run_data, test_automation_token
    )
    automate_sdk = run_function(
        automation_context,
        automate_function,
        FunctionInputs(
            percentage_mean_cutoff=60,
        ),
    )

    assert automate_sdk.run_status == AutomationStatus.SUCCEEDED
