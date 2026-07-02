from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

InputSchemaT = TypeVar("InputSchemaT", bound=BaseModel)
OutputSchemaT = TypeVar("OutputSchemaT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class PromptTemplate(Generic[InputSchemaT, OutputSchemaT]):
    name: str
    version: str
    system_prompt_key: str
    user_prompt_template: str
    input_schema: type[InputSchemaT]
    output_schema: type[OutputSchemaT]
    temperature: float = 0.2
    max_tokens: int | None = None
