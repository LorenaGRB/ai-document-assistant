from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

#It is like a constant object, it can not be changed after it is created. 
# It is used to represent a message in a chat conversation, with a role (either user or assistant) and the content of the message.
@dataclass(frozen=True)
class Message:
    role: Role
    content: str
