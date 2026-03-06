from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    feedback: str