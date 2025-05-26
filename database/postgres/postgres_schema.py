from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(primary_key=True)
    email: str
    name: str
    given_name: str
    family_name: str
    picture: str


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: str = Field(primary_key=True)
    user_id: str
    institution_id: str
    name: str
    subtype: str
    type: str


class Institution(SQLModel, table=True):
    __tablename__ = "institutions"
    id: str = Field(primary_key=True)
    user_id: str
    name: str
    access_token: str
