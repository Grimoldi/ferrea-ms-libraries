from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class Library(BaseModel):
    """Library object representation."""

    name: str
    address: str
    fid: str | None = None
    phone: PhoneNumber | None = None
    email: EmailStr | None = None
    latitude: float | None = None
    longitude: float | None = None
