from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, StringConstraints

from app.domain.fields import COMMUNITY_FIELDS, MENTOR_FIELDS

Role = Literal["student", "mentor"]
Minutes = Literal[30, 60, 90, 120]


def _clean(value: Any) -> Any:
    # PostgreSQL text cannot store NUL characters.
    return value.replace("\x00", "").strip() if isinstance(value, str) else value


def _one_of(allowed: tuple[str, ...]) -> AfterValidator:
    def check(value: str) -> str:
        if value not in allowed:
            raise ValueError(f"must be one of: {', '.join(allowed)}")
        return value

    return AfterValidator(check)


Name = Annotated[str, BeforeValidator(_clean), StringConstraints(min_length=1, max_length=60)]
Bio = Annotated[str, BeforeValidator(_clean), StringConstraints(min_length=10, max_length=500)]
Topic = Annotated[str, BeforeValidator(_clean), StringConstraints(min_length=1, max_length=300)]
Body = Annotated[str, BeforeValidator(_clean), StringConstraints(min_length=1, max_length=1500)]
ChatText = Annotated[str, BeforeValidator(_clean), StringConstraints(min_length=1, max_length=2000)]
MentorField = Annotated[str, _one_of(MENTOR_FIELDS)]
CommunityField = Annotated[str, _one_of(COMMUNITY_FIELDS)]


class In(BaseModel):
    """Base for request bodies: unknown keys are rejected."""

    model_config = ConfigDict(extra="forbid")


class Out(BaseModel):
    """Base for responses."""

    model_config = ConfigDict(from_attributes=True)
