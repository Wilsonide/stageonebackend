from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class StringProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: dict[str, int]


class InterpretedQuery(BaseModel):
    filters_applied: dict[str, str | bool | int] = Field(
        default_factory=dict, description="Filters derived from the query"
    )


class NaturalFilter(BaseModel):
    original: str = Field(..., description="The original user query or search string")
    parsed_filters: dict[str, str | bool | int] = Field(
        default_factory=dict,
        description="Filters interpreted from the natural language query",
    )


class StringResponse(BaseModel):
    id: str = Field(..., description="SHA-256 hash value used as the record ID")
    value: str = Field(..., description="Original string that was analyzed")
    properties: StringProperties
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created"
    )

    model_config = ConfigDict(from_attributes=True)

    # ✅ Serialize datetime as ISO 8601 with 'Z'
    @field_serializer("created_at", when_used="always")
    def serialize_created_at(self, value: datetime) -> str:
        # Ensure UTC and format as YYYY-MM-DDTHH:MM:SSZ
        return (
            value.astimezone(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        )


class DataFilterResponse(BaseModel):
    data: list[StringResponse]
    count: int
    filters_applied: InterpretedQuery


class NaturalFilterResponse(BaseModel):
    data: list[StringResponse]
    count: int
    interpreted_query: NaturalFilter


class StringData(BaseModel):
    value: str
