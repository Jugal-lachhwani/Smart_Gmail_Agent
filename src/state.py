from typing import TypedDict,List,Annotated
from pydantic import BaseModel,Field
from langgraph.graph.message import add_messages

class Email(BaseModel):
    id: str = Field(..., description="Unique identifier of the email")
    threadId: str = Field(..., description="Thread identifier of the email")
    messageId: str = Field(..., description="Message identifier of the email")
    references: str = Field(..., description="References of the email")
    sender: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Body content of the email")

class GraphState(TypedDict):
    emails : List[str]
    current_email : Email
    email_category : str
    generated_email : str
    rag_queries : List[str]
    retrived_document : str
    writter_messages : Annotated[List, add_messages]
    sendable : bool
    trials : int