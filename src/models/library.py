from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class Library(BaseModel):
    """Library object representation."""

    name: str
    address: str
    _id: str | None = Field(
        alias="id",
        serialization_alias="id",
        default=None,
    )
    phone: PhoneNumber | None = None
    email: EmailStr | None = None
    latitude: float | None = None
    longitude: float | None = None
