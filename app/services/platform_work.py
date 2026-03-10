from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import PlatformEpic, PlatformInitiative, PlatformStory, PlatformTask


@dataclass
class PlatformContext:
    initiative: str
    scope: str
    drivers: List[str]
    current_state: str
    target_state: str
    constraints: str
    dependencies: List[str]


def _build_workstreams() -> List[Dict[str, str]]:
    return [
        {
            "name": "Architecture",
            "goal": "Target architecture and component boundaries are agreed.",
        },
        {
            "name": "Protocol",
            "goal": "Contracts and interfaces are versioned and backward compatible.",
        },
        {
            "name": "Reliability",
            "goal": "Error budget policy, retries, and resilience tests are implemented.",
        },
        {
            "name": "Benchmark",
            "goal": "Latency, cost, and quality benchmarks are automated with gates.",
        },
        {
            "name": "Ops",
            "goal": "Runbooks, observability dashboards, and alerting are production ready.",
        },
        {
            "name": "Migration",
            "goal": "Phased rollout and rollback with data integrity safeguards.",
        },
    ]


def build_platform_work_package(context: PlatformContext) -> Dict[str, Any]:
    """Create a structured delivery package for platform transformation work."""

    start = date.today()
    rollout_end = start + timedelta(days=21)

    epics = [
        {
            "name": "Architecture modernization",
            "acceptance_criteria": "Architecture review approved by platform and application teams.",
            "stories": [
                {
                    "name": "Define module boundaries",
                    "acceptance_criteria": "Boundaries documented and reflected in package structure.",
                    "tasks": [
                        {
                            "name": "Publish architecture decision record (ADR)",
                            "owner": "Architecture Guild",
                            "acceptance_criteria": "ADR merged and reviewed by 2 engineers.",
                        },
                        {
                            "name": "Update dependency map",
                            "owner": "Platform Engineering",
                            "acceptance_criteria": "All critical dependencies mapped with owners.",
                        },
                    ],
                }
            ],
        },
        {
            "name": "Reliability and ops hardening",
            "acceptance_criteria": "SLO and runbook gates pass before production rollout.",
            "stories": [
                {
                    "name": "Establish SLO gates",
                    "acceptance_criteria": "CI pipeline blocks release when gates fail.",
                    "tasks": [
                        {
                            "name": "Implement API latency/error dashboards",
                            "owner": "SRE",
                            "acceptance_criteria": "p95 latency and error-rate dashboards live in production.",
                        },
                        {
                            "name": "Create rollback runbook",
                            "owner": "On-call Lead",
                            "acceptance_criteria": "Rollback validated in staging in under 15 minutes.",
                        },
                    ],
                }
            ],
        },
    ]

    options = [
        {
            "name": "Incremental refactor",
            "tradeoffs": "Lowest migration risk, moderate delivery speed.",
            "fit": "Best when uptime and compatibility are top priorities.",
        },
        {
            "name": "Parallel platform (strangler)",
            "tradeoffs": "Higher short-term cost, strongest rollback posture.",
            "fit": "Best when large protocol changes are required.",
        },
        {
            "name": "Big-bang replacement",
            "tradeoffs": "Fastest cutover, highest operational risk.",
            "fit": "Only suitable for low criticality environments.",
        },
    ]

    return {
        "context": {
            "initiative": context.initiative,
            "scope": context.scope,
            "drivers": context.drivers,
            "current_state": context.current_state,
            "target_state": context.target_state,
            "constraints": context.constraints,
            "dependencies": context.dependencies,
        },
        "workstreams": _build_workstreams(),
        "recommendation": {
            "chosen_option": "Incremental refactor",
            "reason": "Balances risk and delivery speed while preserving rollback flexibility.",
            "options": options,
        },
        "architecture_protocol_update": [
            "Publish target module diagram and API ownership matrix.",
            "Version protocol schemas and enforce contract testing in CI.",
            "Deprecate legacy endpoints with sunset timeline.",
        ],
        "risk_register": [
            {
                "risk": "Protocol drift between old and new services",
                "failure_mode": "Client incompatibility and elevated 4xx/5xx errors",
                "mitigation": "Contract tests + schema version pinning before each release.",
            },
            {
                "risk": "Insufficient capacity under peak load",
                "failure_mode": "Latency SLO violations",
                "mitigation": "Canary + load test gate requiring p95 < 700ms before full rollout.",
            },
        ],
        "rollout_plan": {
            "owner": "Platform Engineering",
            "timeline": [
                {"phase": "Phase 1 - staging validation", "date": str(start + timedelta(days=7))},
                {"phase": "Phase 2 - 10% canary", "date": str(start + timedelta(days=14))},
                {"phase": "Phase 3 - full rollout", "date": str(rollout_end)},
            ],
            "rollback": "Switch traffic to previous stable version and replay queued writes.",
        },
        "ops_readiness_checklist": [
            "Synthetic probes and SLO alerts configured.",
            "Runbooks available for incident triage and rollback.",
            "On-call handoff and escalation paths confirmed.",
        ],
        "definition_of_done": {
            "tests": "Unit + integration + contract tests pass in CI.",
            "slo_gates": "Error rate < 1%, p95 latency within agreed threshold.",
            "benchmarking_gates": "Cost/request and latency benchmark reports attached to release.",
            "observability": "Dashboards, traces, and alerts validated in production-like environment.",
            "runbooks": "Incident and rollback runbooks approved by on-call leads.",
            "security_checks": "Secrets scanning, dependency audit, and IAM review completed.",
        },
        "backlog": epics,
    }


async def persist_platform_work_package(
    session: AsyncSession,
    context: PlatformContext,
    package: Dict[str, Any],
) -> PlatformInitiative:
    """Persist initiative, epics, stories, and tasks into database tables."""

    initiative = PlatformInitiative(
        name=context.initiative,
        scope=context.scope,
        drivers={"items": context.drivers},
        current_state=context.current_state,
        target_state=context.target_state,
        constraints=context.constraints,
        dependencies={"items": context.dependencies},
    )
    session.add(initiative)
    await session.flush()

    for epic_data in package.get("backlog", []):
        epic = PlatformEpic(
            initiative_id=initiative.id,
            title=epic_data["name"],
            acceptance_criteria=epic_data.get("acceptance_criteria"),
        )
        session.add(epic)
        await session.flush()

        for story_data in epic_data.get("stories", []):
            story = PlatformStory(
                epic_id=epic.id,
                title=story_data["name"],
                acceptance_criteria=story_data.get("acceptance_criteria"),
            )
            session.add(story)
            await session.flush()

            for task_data in story_data.get("tasks", []):
                task = PlatformTask(
                    story_id=story.id,
                    title=task_data["name"],
                    owner=task_data.get("owner"),
                    acceptance_criteria=task_data["acceptance_criteria"],
                )
                session.add(task)

    await session.commit()
    await session.refresh(initiative)
    return initiative
