#!/usr/bin/env python3
"""Validate ReadingMapIR structure and deterministic quality invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Install it with `python3 -m pip install pyyaml`."
    ) from exc


REQUIRED_SECTIONS = (
    "identity",
    "routing",
    "context",
    "author",
    "work",
    "entry",
    "evidence",
    "uncertainty",
    "quality",
)
MODES = {"experience", "argument", "method", "knowledge"}
SCOPES = {"metadata_only", "pre_reading", "text_grounded"}
CLAIM_TYPES = {
    "fact",
    "accepted_interpretation",
    "system_inference",
    "open_question",
}
GATE_KEYS = (
    "gate_0_identity",
    "gate_1_routing",
    "gate_2_evidence",
    "gate_3_causal_links",
    "gate_4_overinterpretation",
    "gate_5_summary_drift",
    "gate_6_reading_value",
    "gate_7_completeness",
)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Reading Coach ReadingMapIR YAML file."
    )
    parser.add_argument("path", type=Path, help="Path to ReadingMapIR YAML")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as validation failures",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the validation report as JSON",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    try:
        raw = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {args.path}: {exc}")
        return emit(args, errors, warnings)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"invalid YAML: {exc}")
        return emit(args, errors, warnings)

    if not isinstance(data, dict):
        errors.append("document root must be a mapping")
        return emit(args, errors, warnings)

    for section in REQUIRED_SECTIONS:
        if section not in data:
            errors.append(f"missing required section: {section}")

    if errors:
        return emit(args, errors, warnings)

    validate_identity(data["identity"], errors, warnings)
    validate_routing(data["routing"], errors)
    validate_context(data["context"], errors)
    validate_author(data["author"], errors, warnings)
    validate_work(data["work"], errors)
    validate_entry(data["entry"], errors)
    validate_evidence(data["evidence"], errors, warnings)
    validate_uncertainty(data["uncertainty"], errors)
    validate_quality(data["quality"], errors)
    validate_cross_section_rules(data, errors, warnings)

    return emit(args, errors, warnings)


def validate_identity(
    identity: Any, errors: list[str], warnings: list[str]
) -> None:
    if not isinstance(identity, dict):
        errors.append("identity must be a mapping")
        return

    for key in ("title_zh", "author"):
        if not nonempty_string(identity.get(key)):
            errors.append(f"identity.{key} must be a non-empty string")

    confidence = identity.get("identification_confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("identity.identification_confidence must be a number")
    elif not 0 <= confidence <= 1:
        errors.append("identity.identification_confidence must be between 0 and 1")
    elif confidence < 0.8:
        warnings.append("book identity confidence is below the 0.8 release gate")

    scope = identity.get("analysis_scope")
    if scope not in SCOPES:
        errors.append(f"identity.analysis_scope must be one of {sorted(SCOPES)}")


def validate_routing(routing: Any, errors: list[str]) -> None:
    if not isinstance(routing, dict):
        errors.append("routing must be a mapping")
        return

    primary = routing.get("primary_mode")
    secondary = routing.get("secondary_mode")
    if primary not in MODES:
        errors.append(f"routing.primary_mode must be one of {sorted(MODES)}")
    if secondary is not None and secondary not in MODES:
        errors.append("routing.secondary_mode must be null or a supported mode")
    if secondary == primary:
        errors.append("routing.secondary_mode must differ from primary_mode")

    weights: list[int] = []
    for key in ("context_weight", "author_weight", "work_weight"):
        value = routing.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"routing.{key} must be an integer")
            continue
        if not 1 <= value <= 100:
            errors.append(f"routing.{key} must be between 1 and 100")
        weights.append(value)
    if len(weights) == 3 and sum(weights) != 100:
        errors.append("routing weights must sum to 100")

    confidence = routing.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("routing.confidence must be a number")
    elif confidence < 0.75:
        errors.append("routing.confidence is below the 0.75 release gate")

    for key in ("reader_promise", "routing_reason"):
        if not nonempty_string(routing.get(key)):
            errors.append(f"routing.{key} must be a non-empty string")


def validate_context(context: Any, errors: list[str]) -> None:
    if not isinstance(context, dict):
        errors.append("context must be a mapping")
        return
    for key in (
        "relevant_environment",
        "central_tensions",
        "impact_on_people",
        "bridge_to_book",
    ):
        if not nonempty_list(context.get(key)):
            errors.append(f"context.{key} must contain at least one item")


def validate_author(
    author: Any, errors: list[str], warnings: list[str]
) -> None:
    if not isinstance(author, dict):
        errors.append("author must be a mapping")
        return
    for key in (
        "relevant_life_events",
        "recurring_questions",
        "author_lens",
        "thinking_and_expression_style",
        "links_to_work",
        "limitations",
    ):
        if key not in author or not isinstance(author[key], list):
            errors.append(f"author.{key} must be a list")
    if isinstance(author.get("relevant_life_events"), list):
        for index, event in enumerate(author["relevant_life_events"]):
            if not isinstance(event, dict):
                errors.append(f"author.relevant_life_events[{index}] must be a mapping")
                continue
            if not nonempty_string(event.get("relevance_to_book")):
                errors.append(
                    f"author.relevant_life_events[{index}] lacks relevance_to_book"
                )
    if not author.get("relevant_life_events") and not author.get("limitations"):
        warnings.append("empty author evidence must be explained in author.limitations")


def validate_work(work: Any, errors: list[str]) -> None:
    if not isinstance(work, dict):
        errors.append("work must be a mapping")
        return
    for key in ("core_question", "reader_promise", "central_thesis_or_experience"):
        if not nonempty_string(work.get(key)):
            errors.append(f"work.{key} must be a non-empty string")
    if not nonempty_list(work.get("reading_focus")):
        errors.append("work.reading_focus must contain at least one item")
    if not nonempty_list(work.get("likely_misreadings")):
        errors.append("work.likely_misreadings must contain at least one item")
    else:
        for index, item in enumerate(work["likely_misreadings"]):
            if not isinstance(item, dict):
                errors.append(f"work.likely_misreadings[{index}] must be a mapping")
                continue
            if not nonempty_string(item.get("misunderstanding")):
                errors.append(
                    f"work.likely_misreadings[{index}].misunderstanding is required"
                )
            if not nonempty_string(item.get("correction")):
                errors.append(
                    f"work.likely_misreadings[{index}].correction is required"
                )


def validate_entry(entry: Any, errors: list[str]) -> None:
    if not isinstance(entry, dict):
        errors.append("entry must be a mapping")
        return
    for key in ("one_sentence_positioning", "context_author_work_chain"):
        if not nonempty_string(entry.get(key)):
            errors.append(f"entry.{key} must be a non-empty string")
    for key in (
        "before_reading",
        "while_reading",
        "do_not_force",
        "stop_and_think_questions",
    ):
        if not isinstance(entry.get(key), list):
            errors.append(f"entry.{key} must be a list")
    if not nonempty_list(entry.get("while_reading")):
        errors.append("entry.while_reading must contain at least one item")
    if not nonempty_list(entry.get("stop_and_think_questions")):
        errors.append(
            "entry.stop_and_think_questions must contain at least one item"
        )

    boundary = entry.get("transfer_boundary")
    if not isinstance(boundary, dict):
        errors.append("entry.transfer_boundary must be a mapping")
        return
    for key in ("useful_insight", "misuse_risk"):
        if not nonempty_string(boundary.get(key)):
            errors.append(f"entry.transfer_boundary.{key} must be non-empty")


def validate_evidence(
    evidence: Any, errors: list[str], warnings: list[str]
) -> None:
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        return
    if not evidence:
        warnings.append("evidence is empty")
        return

    claim_ids: set[str] = set()
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be a mapping")
            continue
        claim_id = item.get("claim_id")
        if not nonempty_string(claim_id):
            errors.append(f"evidence[{index}].claim_id is required")
        elif claim_id in claim_ids:
            errors.append(f"duplicate evidence claim_id: {claim_id}")
        else:
            claim_ids.add(claim_id)

        claim_type = item.get("claim_type")
        if claim_type not in CLAIM_TYPES:
            errors.append(
                f"evidence[{index}].claim_type must be one of {sorted(CLAIM_TYPES)}"
            )
        if not nonempty_string(item.get("claim")):
            errors.append(f"evidence[{index}].claim is required")
        if claim_type in {
            "fact",
            "accepted_interpretation",
        } and not nonempty_string(item.get("source_title")):
            warnings.append(
                f"evidence[{index}] is {claim_type} but has no source_title"
            )
        if claim_type == "system_inference" and not item.get("supports"):
            warnings.append(
                f"evidence[{index}] is an inference but has no supporting claim IDs"
            )


def validate_uncertainty(uncertainty: Any, errors: list[str]) -> None:
    if not isinstance(uncertainty, list):
        errors.append("uncertainty must be a list")
        return
    for index, item in enumerate(uncertainty):
        if not isinstance(item, dict):
            errors.append(f"uncertainty[{index}] must be a mapping")
            continue
        for key in ("issue", "impact", "action"):
            if not nonempty_string(item.get(key)):
                errors.append(f"uncertainty[{index}].{key} must be non-empty")


def validate_quality(quality: Any, errors: list[str]) -> None:
    if not isinstance(quality, dict):
        errors.append("quality must be a mapping")
        return
    status = quality.get("status")
    if status not in {"pass", "blocked"}:
        errors.append("quality.status must be pass or blocked")
    gates = quality.get("gates")
    if not isinstance(gates, dict):
        errors.append("quality.gates must be a mapping")
        return
    for key in GATE_KEYS:
        if gates.get(key) not in {"pass", "fail"}:
            errors.append(f"quality.gates.{key} must be pass or fail")
    if status == "pass" and any(gates.get(key) != "pass" for key in GATE_KEYS):
        errors.append("quality.status cannot pass while any gate is not pass")
    if status == "blocked" and all(gates.get(key) == "pass" for key in GATE_KEYS):
        errors.append("quality.status cannot be blocked while all gates pass")


def validate_cross_section_rules(
    data: dict[str, Any], errors: list[str], warnings: list[str]
) -> None:
    identity = data["identity"]
    quality = data["quality"]
    scope = identity.get("analysis_scope") if isinstance(identity, dict) else None
    confidence = (
        identity.get("identification_confidence")
        if isinstance(identity, dict)
        else None
    )

    if (
        isinstance(confidence, (int, float))
        and confidence < 0.8
        and quality.get("status") == "pass"
    ):
        errors.append("quality cannot pass when identity confidence is below 0.8")

    if scope == "metadata_only" and quality.get("status") == "pass":
        errors.append("metadata_only analysis cannot be released as a full reading map")

    if scope == "pre_reading" and not data.get("uncertainty"):
        warnings.append(
            "pre_reading analysis has no uncertainty; confirm that text-level claims are absent"
        )


def emit(
    args: argparse.Namespace, errors: list[str], warnings: list[str]
) -> int:
    failed = bool(errors) or (args.strict and bool(warnings))
    report = {
        "status": "fail" if failed else "pass",
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report["status"].upper())
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
