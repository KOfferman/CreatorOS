from __future__ import annotations

from dataclasses import dataclass, field

from .types import PromptTemplate


class PromptTemplateNotFoundError(KeyError):
    pass


@dataclass(slots=True)
class PromptRegistry:
    _templates: dict[tuple[str, str], PromptTemplate] = field(default_factory=dict)

    def register(self, template: PromptTemplate) -> None:
        key = (template.name, template.version)
        self._templates[key] = template

    def get(self, *, name: str, version: str) -> PromptTemplate:
        key = (name, version)
        if key not in self._templates:
            raise PromptTemplateNotFoundError(f"Template not found: {name}:{version}")
        return self._templates[key]
