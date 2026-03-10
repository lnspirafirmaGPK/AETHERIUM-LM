import asyncio

from app.services.platform_work import (
    PlatformContext,
    build_platform_work_package,
    persist_platform_work_package,
)


class FakeSession:
    def __init__(self):
        self.items = []
        self._id = 1
        self.committed = False

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._id
            self._id += 1
        self.items.append(obj)

    async def flush(self):
        return None

    async def commit(self):
        self.committed = True

    async def refresh(self, _):
        return None


def test_build_platform_work_package_contains_required_sections():
    context = PlatformContext(
        initiative="Reliability uplift",
        scope="services/modules/infra",
        drivers=["reliability", "latency", "security"],
        current_state="basic async orchestration",
        target_state="production-gated platform workflow",
        constraints="SLO: p95 < 700ms, budget fixed",
        dependencies=["platform team", "SRE", "data team"],
    )

    package = build_platform_work_package(context)

    assert len(package["workstreams"]) == 6
    assert package["recommendation"]["chosen_option"] == "Incremental refactor"
    assert "definition_of_done" in package
    assert package["backlog"][0]["stories"][0]["tasks"][0]["acceptance_criteria"]


def test_persist_platform_work_package_creates_hierarchy():
    context = PlatformContext(
        initiative="Migration hardening",
        scope="services",
        drivers=["reliability"],
        current_state="single-stage delivery",
        target_state="canary rollout with rollback gates",
        constraints="timeline 3 weeks",
        dependencies=["SRE"],
    )
    package = build_platform_work_package(context)
    session = FakeSession()

    initiative = asyncio.run(persist_platform_work_package(session, context, package))

    assert initiative.name == "Migration hardening"
    assert session.committed is True
    assert len(session.items) >= 4
