from rules.schema.category_rule_spec import CategoryRuleSpec


class PromptRenderer:
    """Renders a CategoryRuleSpec into the two system prompt strings."""

    @staticmethod
    def render_close_cancel(spec: CategoryRuleSpec) -> str:
        category_upper = spec.category.value.upper()
        has_defaults = spec.defaults.reason is not None or spec.defaults.notes

        parts: list[str] = []

        # Role preamble
        parts.append(
            f"You are a claim processing assistant handling {category_upper} items. "
            f"{spec.description}\n\n"
        )

        # Closing rules
        if has_defaults:
            parts.append("CLOSING RULES (task was completed successfully):\n")
        else:
            parts.append("CLOSING RULES:\n")

        for rule in spec.close_rules:
            if rule.applies_to:
                line = f"- For {rule.applies_to}: close when {rule.when}."
            else:
                prefix = f"a {spec.category.value}" if not has_defaults else "an"
                line = f"- Close {prefix} item when {rule.when}."
            if rule.detail:
                line += f" {rule.detail}"
            parts.append(line + "\n")

        parts.append("\n")

        # Cancellation rules
        if has_defaults:
            parts.append("CANCELLATION RULES (task became unnecessary):\n")
        else:
            parts.append("CANCELLATION RULES:\n")

        for rule in spec.cancel_rules:
            if rule.never:
                parts.append(f"- Do NOT cancel {rule.never}.\n")
            elif rule.when:
                if rule.applies_to:
                    line = f"- Cancel {rule.applies_to} when {rule.when}."
                else:
                    prefix = f"a {spec.category.value}" if not has_defaults else "an"
                    line = f"- Cancel {prefix} item when {rule.when}."
                if rule.example:
                    line += f" (e.g., {rule.example})"
                parts.append(line + "\n")

        parts.append("\n")

        # Defaults / IMPORTANT section
        if has_defaults:
            parts.append("IMPORTANT:\n")
            if spec.defaults.reason:
                parts.append(
                    f"- When in doubt, leave the item open. {spec.defaults.reason}\n"
                )
            if spec.defaults.notes:
                for note in spec.defaults.notes:
                    parts.append(f"- {note}\n")
            parts.append("\n")

        # Footer
        parts.append(
            f"Examine the provided claim event against the current open "
            f"{spec.category.value} items. "
            f"Call close_todo_item or cancel_todo_item for each item that should be "
            f"closed or cancelled. If no items need to be closed or cancelled, "
            f"do nothing."
        )

        return "".join(parts)

    @staticmethod
    def render_open_items(spec: CategoryRuleSpec) -> str:
        category_upper = spec.category.value.upper()
        open_rules = spec.open_rules
        has_subsections = (
            any(t.mandatory for t in open_rules.triggers)
            or open_rules.duplication_rules
            or any(t.action for t in open_rules.triggers)
        )

        parts: list[str] = []

        # Role preamble
        parts.append(
            f"You are a claim processing assistant handling {category_upper} items. "
            f"{spec.description}\n\n"
        )

        # Opening rules header
        parts.append("OPENING RULES:\n")

        if open_rules.preamble:
            parts.append(f"{open_rules.preamble}\n\n")

        # Separate triggers by type
        mandatory_triggers = [t for t in open_rules.triggers if t.mandatory]
        action_triggers = [
            t for t in open_rules.triggers if t.action and not t.mandatory
        ]
        simple_triggers = [
            t
            for t in open_rules.triggers
            if not t.mandatory and not t.action
        ]

        # Mandatory triggers subsection
        if mandatory_triggers:
            parts.append("MANDATORY RESERVE REVIEW TRIGGERS:\n")
            parts.append(
                "A reserve review item MUST be opened when any of the following "
                "material circumstance changes appear in the event. This is "
                "non-discretionary:\n"
            )
            for trigger in mandatory_triggers:
                parts.append(f"- {trigger.when}.\n")
            # Description format from duplication rules
            if open_rules.duplication_rules:
                for name, dup_set in open_rules.duplication_rules.items():
                    if dup_set.description_format:
                        parts.append(f"{dup_set.description_format}\n")
            parts.append("\n")

        # Duplication rules subsection
        if open_rules.duplication_rules:
            for name, dup_set in open_rules.duplication_rules.items():
                parts.append(f"{name}:\n")
                preamble_text = (
                    "Before opening a reserve review item, check the open_items "
                    "and accumulated_delta for existing reserve review items.\n"
                )
                parts.append(preamble_text)
                for rule in dup_set.rules:
                    parts.append(f"- {rule}\n")
                parts.append("\n")

        # Action triggers (litigation-style "trigger → action")
        if action_triggers:
            parts.append("Valid triggers and the items they produce:\n")
            for trigger in action_triggers:
                parts.append(f"- {trigger.when} \u2192 {trigger.action}.\n")
            parts.append("\n")

        # Simple triggers
        if simple_triggers and not has_subsections:
            for trigger in simple_triggers:
                parts.append(
                    f"- Open a {spec.category.value} item when {trigger.when}.\n"
                )
        elif simple_triggers:
            # Render under a subsection header for complex categories
            other_header = f"OTHER {category_upper} TRIGGERS:\n"
            parts.append(other_header)
            for trigger in simple_triggers:
                parts.append(f"- {trigger.when}.\n")
            parts.append("\n")

        # Exclusions
        if has_subsections:
            parts.append("Do NOT open items for:\n")
            for exclusion in open_rules.exclusions:
                parts.append(f"- {exclusion}\n")
        else:
            for exclusion in open_rules.exclusions:
                parts.append(
                    f"- Do NOT open {spec.category.value} items for {exclusion}\n"
                )
            parts.append(
                "- Do NOT duplicate any existing open items.\n"
            )

        parts.append("\n")

        # Owner guidance
        parts.append(
            "OWNER GUIDANCE:\n"
            "The owner is the party responsible for executing the item. "
            "Valid owners are: adjuster, employer, provider, injured-worker, other.\n"
        )
        for og in spec.owner_guidance:
            parts.append(f"- {og.owner.value}: for {og.when}.\n")

        parts.append("\n")

        # Footer
        parts.append(
            f"Based on the provided claim event, create new {spec.category.value} "
            f"todo items. Use add_open_item to create each new item. "
            f"Valid urgency types are: milestone-protecting, deadline-driven, "
            f"discretionary."
        )

        return "".join(parts)
