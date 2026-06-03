from pydantic import BaseModel, ConfigDict, field_validator


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: str
    message: str
    is_sent: bool
    sent_at: str | None = None
    created_at: str

    @field_validator("sent_at", mode="before")
    @classmethod
    def stringify_sent_at(cls, v):
        return str(v) if v is not None else None

    @field_validator("created_at", mode="before")
    @classmethod
    def stringify_created_at(cls, v):
        return str(v)
