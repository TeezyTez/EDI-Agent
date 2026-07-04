from enum import Enum
from typing import Any
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class MappingStatus(str, Enum):
    AUTO_CONFIRMED = "auto_confirmed"
    NEED_REVIEW = "need_review"
    UNMATCHED = "unmatched"


class RuleType(str, Enum):
    DIRECT = "direct"
    DATE_FORMAT = "date_format"
    ENUM_MAPPING = "enum_mapping"
    SPLIT = "split"
    MERGE = "merge"
    DEFAULT_VALUE = "default_value"


class FieldSchema(BaseModel):
    field_name: str
    description: str = ""
    type: str = "string"
    required: bool = False
    example: Any = None


class FieldMapping(BaseModel):
    source_field: str | None = None
    source_fields: list[str] = Field(default_factory=list)
    target_field: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    rule_type: RuleType = RuleType.DIRECT
    fixed_value: Any = None
    transform_expression: str | None = None
    diagnostics_path: str | None = None
    status: MappingStatus


class TransformRule(BaseModel):
    source_field: str | None = None
    target_field: str
    rule_type: RuleType
    default_value: Any = None
    enum_map: dict[str, Any] = Field(default_factory=dict)
    date_input_format: str | None = None
    date_output_format: str | None = None


class AgentResult(BaseModel):
    mappings: list[FieldMapping]
    rules: list[TransformRule]
    transform_path: str
    test_path: str
    report_path: str
    pytest_passed: bool
    pytest_output: str


class ApiPushResult(BaseModel):
    endpoint: str
    method: str
    mappings: list[FieldMapping]
    payload_template_path: str
    mapping_report_path: str
    mapping_review_path: str = ""
    diagnostics_path: str = ""
    llm_used: bool = False
    llm_message: str = ""


class KnowledgeItem(BaseModel):
    id: str
    title: str
    category: str = "business_context"
    content: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
