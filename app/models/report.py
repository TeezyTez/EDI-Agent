from pydantic import BaseModel


class ReportSection(BaseModel):
    title: str
    body: str
