from workflows.schema.workflow_spec import WorkflowSpec


class WorkflowPromptRenderer:
    """Renders a WorkflowSpec into a single system prompt."""

    @staticmethod
    def render(spec: WorkflowSpec) -> str:
        parts: list[str] = []

        category_label = (
            spec.category.value.upper() if spec.category else spec.workflow_id.upper()
        )

        # Role preamble
        parts.append(
            f"You are a claim processing assistant handling {category_label} items. "
            f"{spec.description}\n\n"
        )

        # Branches
        parts.append("BRANCHES:\n")
        parts.append(
            "Examine the claim event and match it against the following branches. "
            "When a branch matches, follow its instructions to decide which tools to call.\n\n"
        )
        for branch in spec.branches:
            parts.append(f'Branch "{branch.name}":\n')
            parts.append(f"  Trigger: {branch.trigger}\n")
            parts.append(f"  Instructions: {branch.instructions}\n\n")

        # Exclusions
        if spec.exclusions:
            parts.append("EXCLUSIONS:\n")
            parts.append("Do NOT act on:\n")
            for exclusion in spec.exclusions:
                parts.append(f"- {exclusion}\n")
            parts.append("\n")

        # Owner guidance
        if spec.owner_guidance:
            parts.append(
                "OWNER GUIDANCE:\n"
                "The owner is the party responsible for executing the item. "
                "Valid owners are: adjuster, employer, provider, injured-worker, other.\n"
            )
            for og in spec.owner_guidance:
                parts.append(f"- {og.owner.value}: for {og.when}.\n")
            parts.append("\n")

        # Defaults
        if spec.defaults.reason or spec.defaults.notes:
            parts.append("IMPORTANT:\n")
            if spec.defaults.reason:
                parts.append(
                    f"- When in doubt, leave the item open. {spec.defaults.reason}\n"
                )
            if spec.defaults.notes:
                for note in spec.defaults.notes:
                    parts.append(f"- {note}\n")
            parts.append("\n")

        # Tool instructions
        parts.append(
            "AVAILABLE TOOLS:\n"
            "- add_open_item: Create a new open todo item. Provide todo_item_id, "
            "description, owner, urgency_type (milestone-protecting, deadline-driven, "
            "or discretionary), sub_category, and optionally due_on (YYYY-MM-DD) "
            "and context_entity_id (link to an entity).\n"
            "- close_todo_item: Close an open item by its ID.\n"
            "- cancel_todo_item: Cancel an open item by its ID.\n"
            "- create_entity: Create a new entity (diagnosis or treatment). "
            "Provide entity_id, entity_type (diagnosis or treatment), and description.\n"
            "- update_entity: Update an existing entity's description. "
            "Provide entity_id and the new description.\n"
            "- delete_entity: Supersede an entity by its ID. "
            "The entity remains in state with status superseded.\n"
            "- start_workflow: Start a sub-workflow by its workflow_id.\n\n"
        )

        # Reasoning instructions
        parts.append(
            "PROCEDURE:\n"
            "Before calling any tools, think step-by-step and output your reasoning:\n"
            "1. Summarize the claim event in one sentence.\n"
            "2. List each branch and state whether it matches or not, with a brief reason.\n"
            "3. For each matched branch, list the specific tool calls you will make "
            "and why (e.g. which items to close, what new items to create, "
            "which entities to create or update).\n"
            "4. Execute the tool calls.\n"
            "If no branches match, state that explicitly and do nothing.\n"
        )

        return "".join(parts)
