"""
Validation request
"""
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import isodate
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator
from typing import Union


class RequestSave(BaseModel):
    """
    RequestSave
    """
    conversation_id: uuid.UUID
    user_id: Union[uuid.UUID, None]
    user_name: str = ""
    save_chat: bool = False
    language: str = 'Spanish'
    message: list = []
    access_token: str = ""
    token_id: str = ""

class RequestCleaning(BaseModel):
    """
    RequestCleaning
    """
    user_id: uuid.UUID
    access_token: str = ""
    token_id: str = ""

class RequestDelete(BaseModel):
    """
    RequestDelete
    """
    delete: bool = False
    conversation_id: uuid.UUID
    access_token: str = ""
    token_id: str = ""

class Message(BaseModel):
    """
    Message
    """
    id: int
    author: str
    content: str
    datetime: datetime

class RequestHistoricalMessage(BaseModel):
    """
    RequestHistoricalMessage
    """
    messages: List[Message]

class RequestTopic(BaseModel):
    """
    RequestTopic
    """
    conversation_id: uuid.UUID
    topic: str
    created_at: datetime
    modified_at: datetime

class RequestUpdateTopic(BaseModel):
    """
    RequestUpdateTopic
    """
    topic: str
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    access_token: str = ""
    token_id: str = ""

class User(BaseModel):
    """
    User
    """
    id: Optional[int] = Field(alias='id')
    user_id: str = Field(alias='user_id')
    username: Optional[str] = Field(alias='username')
    created_at: Optional[datetime] = Field(alias='created_at')

class Conversation(BaseModel):
    """
    Conversation
    """
    id: Optional[int] = Field(alias='id')
    conversation_id: str = Field(alias='conversation_id')
    user_id: str = Field(alias='user_id')
    topic: Optional[str] = Field(alias='topic')
    save_chat: Optional[bool] = Field(alias='save_chat')
    language: Optional[str] = Field(alias='language')
    created_at: Optional[datetime] = Field(alias='created_at')
    modified_at: Optional[datetime] = Field(alias='modified_at')
