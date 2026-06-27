"""Best-effort data warmup for hosted Render builds.

The app works without these caches, but preparing them during the image build lets
Render serve a useful live-proxy demo without relying on this machine's local
`data/` directory. Every step fails soft so a temporary upstream outage does not
break deployment.
"""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path

from skillsmarket.ingest_mcf import run_live_snapshot
from skillsmarket.live_evidence import build_evidence_aggregate, write_evidence
from skillsmarket.skillsfuture import build_course_index, download_course_rows, write_courses
from skillsmarket.skill_catalog import catalog_skill_names


def prepare_mycareersfuture() -> None:
    result = run_live_snapshot(pages=2, limit=30)
    snapshots = sorted(glob.glob("data/raw/mycareersfuture/mcf-*.json"), key=os.path.getmtime)
    if not snapshots:
        print("MyCareersFuture warmup: no snapshot written")
        return
    payload = json.loads(Path(snapshots[-1]).read_text())
    write_evidence(build_evidence_aggregate(payload.get("records") or []))
    print(f"MyCareersFuture warmup: {result.get('record_count')} jobs")


def prepare_skillsfuture() -> None:
    courses = download_course_rows()
    write_courses(build_course_index(catalog_skill_names(), courses))
    print(f"SkillsFuture warmup: {len(courses)} courses")


def main() -> None:
    for label, fn in [
        ("mycareersfuture", prepare_mycareersfuture),
        ("skillsfuture", prepare_skillsfuture),
    ]:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - deploy must not fail on upstream data outage.
            print(f"{label} warmup skipped: {exc}")


if __name__ == "__main__":
    main()
