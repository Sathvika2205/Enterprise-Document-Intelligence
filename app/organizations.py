import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

REGISTRY_PATH = Path("data/organizations.json")
RAW_DATA_DIR = Path("data/raw")


class Organization(BaseModel):
    id: str
    name: str
    created_at: str


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "org"


def _load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []

    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _save_registry(orgs: list[dict]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(orgs, indent=2),
        encoding="utf-8",
    )


def list_organizations() -> list[Organization]:
    return [
        Organization(**org)
        for org in sorted(
            _load_registry(),
            key=lambda org: org["name"].lower(),
        )
    ]


def get_organization(org_id: str) -> Optional[Organization]:
    for org in list_organizations():
        if org.id == org_id:
            return org

    return None


def create_organization(name: str) -> Organization:
    name = name.strip()

    if not name:
        raise ValueError("Organization name cannot be empty.")

    orgs = _load_registry()

    if any(org["name"].lower() == name.lower() for org in orgs):
        raise ValueError(f"An organization named '{name}' already exists.")

    base_slug = _slugify(name)
    slug = base_slug
    existing_ids = {org["id"] for org in orgs}

    counter = 2

    while slug in existing_ids:
        slug = f"{base_slug}_{counter}"
        counter += 1

    org = Organization(
        id=slug,
        name=name,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    orgs.append(org.model_dump())
    _save_registry(orgs)

    organization_raw_dir(org.id)

    return org


def organization_raw_dir(org_id: str) -> Path:
    path = RAW_DATA_DIR / org_id
    path.mkdir(parents=True, exist_ok=True)
    return path
