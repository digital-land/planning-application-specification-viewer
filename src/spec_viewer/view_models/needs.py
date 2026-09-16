"""Legacy-compatible need relationship display; package gap PKG-07."""
from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional

def extract_dataset_only_refs(blob: Any) -> List[str]:
    """
    Return dataset refs only from entries that specify a dataset alone (no field).
    For satisfied_by lists, this means items that are dicts with a dataset key and
    no other populated keys (or only dataset populated).
    """
    refs: List[str] = []
    if isinstance(blob, dict):
        keys_with_values = [k for k, v in blob.items() if v]
        if "dataset" in blob and isinstance(blob["dataset"], str):
            if len(keys_with_values) == 1 and keys_with_values[0] == "dataset":
                refs.append(blob["dataset"])
    elif isinstance(blob, list):
        for item in blob:
            refs.extend(extract_dataset_only_refs(item))
    return refs

def build_need_maps(
    needs_data: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
    needs = needs_data.get("need", {})
    justifications = needs_data.get("justification", {})

    need_to_justifications: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    dataset_to_need_justifications: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for justification in justifications.values():
        need_ids = justification.get("needs", [])
        satisfied_by = justification.get("satisfied_by", {})
        datasets = extract_dataset_only_refs(satisfied_by)
        for n_id in need_ids:
            need_to_justifications[n_id].append(justification)
            # Attach to datasets that are satisfied purely by dataset references
            for dataset in datasets:
                dataset_to_need_justifications[dataset].append(
                    {"need": n_id, "justification": justification}
                )
    return need_to_justifications, dataset_to_need_justifications

def join_list_phrases(items: List[str], conj: str = "and") -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" {conj} " + items[-1]

def satisfaction_messages_for_field(
    all_need_justs: List[Tuple[str, Dict[str, Any]]],
    current_dataset: str,
    current_field: str,
    url_for,
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []

    def label_item(item: Dict[str, Any]) -> Optional[str]:
        ds = item.get("dataset")
        field = item.get("field")
        if not field:
            return None
        ds_link = (
            f'<a class="govuk-link" href="{url_for(f"/dataset/{ds}")}">{ds}</a>'
            if ds
            else ""
        )
        field_code = f"<code class='app-code'>{field}</code>"
        if ds and ds != current_dataset:
            return f"field {field_code} (dataset {ds_link})"
        return f"field {field_code}"

    def process_group(
        items: List[Dict[str, Any]], connector: str, need_id: str, need_href: str
    ) -> Optional[str]:
        current_in_group = False
        other_labels: List[str] = []
        for it in items:
            ds = it.get("dataset")
            field = it.get("field")
            if ds == current_dataset and field == current_field:
                current_in_group = True
            else:
                lbl = label_item(it)
                if lbl:
                    other_labels.append(lbl)
        if not current_in_group:
            return None
        if connector == "and":
            if other_labels:
                return f"This field and {join_list_phrases(other_labels, 'and')} satisfy need <a class=\"govuk-link\" href=\"{need_href}\">{need_id}</a>."
            return f'This field satisfies need <a class="govuk-link" href="{need_href}">{need_id}</a>.'
        else:
            if other_labels:
                return f"This field or {join_list_phrases(other_labels, 'or')} satisfy need <a class=\"govuk-link\" href=\"{need_href}\">{need_id}</a>."
            return f'This field satisfies need <a class="govuk-link" href="{need_href}">{need_id}</a>.'

    for need_id, justification in all_need_justs:
        sb = justification.get("satisfied_by")
        need_href = url_for(f"/user-need/{need_id}")

        # List of simple dicts (dataset/field)
        if isinstance(sb, list):
            msg = process_group(sb, "and", need_id, need_href)
            if msg:
                messages.append({"text": msg})
            continue

        if isinstance(sb, dict):
            if "allOf" in sb and isinstance(sb["allOf"], list):
                # handle nested anyOf within allOf
                current_matched = False
                other_labels: List[str] = []
                nested_msgs: List[str] = []
                for clause in sb["allOf"]:
                    if isinstance(clause, dict) and "anyOf" in clause:
                        any_msg = process_group(
                            clause["anyOf"], "or", need_id, need_href
                        )
                        if any_msg:
                            nested_msgs.append(
                                any_msg.replace("This field", "One of these fields")
                            )
                            current_matched = True
                        else:
                            # collect other labels for summary text
                            for it in clause["anyOf"]:
                                lbl = label_item(it)
                                if lbl:
                                    other_labels.append(lbl)
                    elif isinstance(clause, dict):
                        ds = clause.get("dataset")
                        field = clause.get("field")
                        if ds == current_dataset and field == current_field:
                            current_matched = True
                        else:
                            lbl = label_item(clause)
                            if lbl:
                                other_labels.append(lbl)
                if current_matched:
                    if other_labels:
                        messages.append(
                            {
                                "text": f"This field and {join_list_phrases(other_labels, 'and')} satisfy need <a class=\"govuk-link\" href=\"{need_href}\">{need_id}</a>."
                            }
                        )
                    elif not nested_msgs:
                        messages.append(
                            {
                                "text": f'This field helps satisfy need <a class="govuk-link" href="{need_href}">{need_id}</a>.'
                            }
                        )
                    messages.extend([{"text": m} for m in nested_msgs])
                continue

            if "anyOf" in sb and isinstance(sb["anyOf"], list):
                msg = process_group(sb["anyOf"], "or", need_id, need_href)
                if msg:
                    messages.append({"text": msg})
                continue

            # rule-based not tied to a specific field
            continue

    return messages


def need_status(justifications: List[Dict[str, Any]]) -> Tuple[str, str]:
    satisfaction = {j.get("satisfaction", "").lower() for j in justifications}
    if "full" in satisfaction:
        return "Satisfied", "govuk-tag--green"
    if "partial" in satisfaction:
        return "Partially satisfied", "govuk-tag--blue"
    if satisfaction:
        return "Proposed", "govuk-tag--yellow"
    return "Not satisfied", "govuk-tag--grey"

def need_status_dict(justifications: List[Dict[str, Any]]) -> Dict[str, str]:
    label, cls = need_status(justifications)
    return {"tag_label": label, "tag_class": cls}

def build_need_meta(need: Dict[str, Any]) -> List[Dict[str, str]]:
    meta: List[Dict[str, str]] = []
    if need.get("priority"):
        meta.append({"label": "Priority", "value": need.get("priority")})
    if need.get("status"):
        meta.append({"label": "Status", "value": need.get("status")})
    if need.get("themes"):
        meta.append({"label": "Themes", "value": ", ".join(need.get("themes"))})
    if need.get("actors"):
        meta.append({"label": "Actors", "value": ", ".join(need.get("actors"))})
    if need.get("source"):
        sources = need.get("source")
        formatted_sources = (
            ", ".join([s.get("type", "") for s in sources])
            if isinstance(sources, list)
            else str(sources)
        )
        meta.append({"label": "Source", "value": formatted_sources})
    if need.get("variations"):
        meta.append(
            {
                "label": "Variations",
                "value": ", ".join([str(v) for v in need.get("variations") if v]),
            }
        )
    if need.get("next_step"):
        meta.append({"label": "Next step", "value": need.get("next_step")})
    return meta

def justification_search_references(blob: Any) -> List[str]:
    """Collect labelled references from nested satisfaction conditions."""
    refs = []
    if isinstance(blob, dict):
        for key, value in blob.items():
            if key in {"dataset", "field", "codelist", "module", "component"} and isinstance(value, str):
                refs.append(f"{key.capitalize()}: {value}")
            elif key == "includes" and isinstance(value, list):
                refs.extend(f"Code: {code}" for code in value if isinstance(code, str))
            elif isinstance(value, (dict, list)):
                refs.extend(justification_search_references(value))
    elif isinstance(blob, list):
        for item in blob:
            refs.extend(justification_search_references(item))
    return list(dict.fromkeys(refs))
