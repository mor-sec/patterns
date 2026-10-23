"""Versioned reference data: the threat library and the control crosswalk."""

from __future__ import annotations

from functools import cached_property
from importlib import resources
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from tra_core.schemas import Stride


class LibraryThreat(BaseModel):
    id: str
    title: str
    stride: list[Stride]
    applies_to: list[str]
    tags: list[str] = Field(default_factory=list)
    atlas: list[str] = Field(default_factory=list)
    sar_ref: list[str] = Field(default_factory=list)
    description: str
    controls: list[str] = Field(default_factory=list)


class CommonControl(BaseModel):
    id: str
    title: str
    domain: str
    iso27001: list[str] = Field(default_factory=list)
    e8: list[str] = Field(default_factory=list)
    asd_essentials: list[str] = Field(default_factory=list)
    ism: list[str] = Field(default_factory=list)
    pci_dss: list[str] = Field(default_factory=list)

    def references(self) -> dict[str, list[str]]:
        return {
            k: v
            for k, v in {
                "ISO 27001": self.iso27001,
                "E8": self.e8,
                "ASD Essentials": self.asd_essentials,
                "ISM": self.ism,
                "PCI DSS": self.pci_dss,
            }.items()
            if v
        }


def _load_yaml(name: str, path: Path | None) -> dict[str, Any]:
    if path is not None:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    text = resources.files("tra_core.data").joinpath(name).read_text(encoding="utf-8")
    return yaml.safe_load(text)


class ThreatLibrary:
    def __init__(self, path: Path | None = None) -> None:
        raw = _load_yaml("threat_library.yaml", path)
        self.meta: dict[str, Any] = raw.get("meta", {})
        self.threats = [LibraryThreat.model_validate(t) for t in raw["threats"]]
        self._by_id = {t.id: t for t in self.threats}

    @property
    def version(self) -> str:
        return str(self.meta.get("version", "unversioned"))

    def get(self, threat_id: str) -> LibraryThreat | None:
        return self._by_id.get(threat_id)

    def search(self, applies_to: str, tags: list[str] | None = None, include_ai: bool = False) -> list[LibraryThreat]:
        """Threats that apply to this element kind, filtered by tags.

        AI threats are only returned for AI elements, and every element gets the
        untagged and generic threats for its kind.
        """
        tags = set(tags or [])
        hits = []
        for t in self.threats:
            if applies_to not in t.applies_to:
                continue
            if "ai" in t.tags and not include_ai:
                continue
            if tags and not tags.intersection(t.tags) and "ai" not in t.tags:
                continue
            hits.append(t)
        return hits


class ControlCatalogue:
    def __init__(self, path: Path | None = None) -> None:
        raw = _load_yaml("controls.yaml", path)
        self.meta: dict[str, Any] = raw.get("meta", {})
        self.controls = [CommonControl.model_validate(c) for c in raw["controls"]]
        self._by_id = {c.id: c for c in self.controls}

    @property
    def version(self) -> str:
        return str(self.meta.get("version", "unversioned"))

    def exists(self, control_id: str) -> bool:
        return control_id in self._by_id

    def get(self, control_id: str) -> CommonControl | None:
        return self._by_id.get(control_id)

    def lookup(self, ids: list[str]) -> list[CommonControl]:
        return [self._by_id[i] for i in ids if i in self._by_id]


class Reference:
    """Both reference sets, loaded once."""

    def __init__(self, threats_path: Path | None = None, controls_path: Path | None = None) -> None:
        self._threats_path = threats_path
        self._controls_path = controls_path

    @cached_property
    def threats(self) -> ThreatLibrary:
        return ThreatLibrary(self._threats_path)

    @cached_property
    def controls(self) -> ControlCatalogue:
        return ControlCatalogue(self._controls_path)
