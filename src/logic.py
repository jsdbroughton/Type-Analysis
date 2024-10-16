import math
from collections import defaultdict
from typing import Dict, List, Union

import numpy as np
from speckle_automate import AutomationContext
from specklepy.objects.base import Base
from specklepy.objects.other import BlockInstance

from src.inputs import FunctionInputs


def group_elements(
        elements: Union[List[Base], Base]
) -> Dict[str, List[Base]]:
    """Recursively groups elements by the specified attribute."""
    grouped: Dict[str, List[Base]] = defaultdict(list)

    def extract(inner_elements: Union[List[Base], Base]) -> None:
        if isinstance(inner_elements, list):
            for element in inner_elements:
                if isinstance(element, BlockInstance):
                    key = getattr(element.definition, "name", None)
                    if key:
                        grouped[key].append(element)
                    if hasattr(element, "elements"):
                        extract(element.elements)
        elif hasattr(inner_elements, "elements"):
            extract(inner_elements.elements)

    extract(elements)
    return dict(grouped)


def summarise_types(
        types: Dict[str, List[Base]], label: str, cutoff: int, percentage: float
) -> str:
    """Generates a summary of typical and special types."""
    summary = (
        f"\n{label} Types ({cutoff} occurrences or "
        f"{'more' if 'Typical' in label else 'fewer'}, "
        f"{percentage:.0f}% of the mean):\n"
    )
    summary += "\n".join(f"{name}: {len(elements)}" for name, elements in types.items())
    return summary


def find_all_block_instances(elements: Union[List[Base], Base]) -> List[BlockInstance]:
    """Recursively traverse and find all BlockInstance elements."""
    inner_block_instances: List[BlockInstance] = []

    def traverse(inner_elements: Union[List[Base], Base]) -> None:
        if isinstance(inner_elements, list):
            for element in inner_elements:
                if isinstance(element, BlockInstance):
                    inner_block_instances.append(element)
                elif isinstance(element, Base) and hasattr(element, "elements"):
                    traverse(element.elements)
        elif isinstance(inner_elements, Base) and hasattr(inner_elements, "elements"):
            traverse(inner_elements.elements)

    traverse(elements)
    return inner_block_instances


def automate_function(
        automate_context: AutomationContext,
        function_inputs: FunctionInputs,
) -> None:
    """This is an example Speckle Automate function.

    Args:
        automate_context: A context-helper object that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data that triggered this run.
            It also has convenient methods for attaching result data to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """
    # The context provides a convenient way to receive the triggering version.
    version_root_object = automate_context.receive_version()

    # Find BlockInstance elements in data
    block_instances: List[BlockInstance] = find_all_block_instances(version_root_object)

    # Group BlockInstance elements by definition.name
    grouped_elements: Dict[str, List[Base]] = group_elements(block_instances)

    # Calculate statistics for typical and special types
    mean_elements: np.floating = np.mean(
        [len(elements) for elements in grouped_elements.values()]
    )

    percentage_of_mean_cutoff = function_inputs.percentage_mean_cutoff or 60

    cutoff: int = math.floor(mean_elements * (percentage_of_mean_cutoff / 100))  # 60% cutoff

    typical_types: Dict[str, List[Base]] = {
        name: elements
        for name, elements in grouped_elements.items()
        if len(elements) > cutoff
    }
    special_types: Dict[str, List[Base]] = {
        name: elements
        for name, elements in grouped_elements.items()
        if len(elements) <= cutoff
    }

    typical_summary: str = summarise_types(
        types=typical_types,
        label="Typical",
        cutoff=cutoff,
        percentage=percentage_of_mean_cutoff)

    special_summary: str = summarise_types(
        types=special_types,
        label="Special",
        cutoff=cutoff,
        percentage=percentage_of_mean_cutoff,
    )

    # Collect element IDs for typical and special types
    typical_type_ids: List[str] = [
        element.id for elements in typical_types.values() for element in elements
    ]
    special_type_ids: List[str] = [
        element.id for elements in special_types.values() for element in elements
    ]

    if typical_type_ids:
        automate_context.attach_info_to_objects(
            category="Type Analysis",
            message=f"These fin types are typical.\n\nSummary of Types:\n"
                    f"{typical_summary}",
            object_ids=typical_type_ids,
        )

    if special_type_ids:
        automate_context.attach_warning_to_objects(
            category="Type Analysis",
            message=f"These fin types are special.\n\nSummary of Types:\n"
                    f"{special_summary}",
            object_ids=special_type_ids,
        )

    automate_context.mark_run_success("Fins are cool.")
