from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users" #type: ignore
    id: str = Field(primary_key=True)
    email: str
    name: str
    given_name: str
    family_name: str
    picture: str
    locale: str

class Account(SQLModel, table=True):
    __tablename__ = "accounts" #type: ignore
    id: str = Field(primary_key=True)
    user_id: str
    institution_id: str
    name: str
    sub_type: str
    type: str

class Institution(SQLModel, table=True):
    __tablename__ = "institutions" #type: ignore
    id: str = Field(primary_key=True)
    user_id: str
    name: str
