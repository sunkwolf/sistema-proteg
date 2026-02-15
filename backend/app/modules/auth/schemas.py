from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int = 900
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str | None = None
    role_id: int | None = None
    department_id: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "bearer"
    user: UserInfo
