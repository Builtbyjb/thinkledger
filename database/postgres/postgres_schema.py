from sqlmodel import Field, SQLModel

class User(SQLModel):
    id: str = Field(primary_key=True)
    email: str
    name: str
    given_name: str
    family_name: str
    picture: str
    locale: str

class Account(SQLModel):
    id: str = Field(primary_key=True)
    user_id: str
    institution_id: str
    name: str
    sub_type: str
    type: str

class Institution(SQLModel):
    id: str = Field(primary_key=True)
    user_id: str
    name: str
