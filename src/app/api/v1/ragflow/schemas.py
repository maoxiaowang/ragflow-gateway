from typing import Optional, List

from pydantic import BaseModel, constr, Field

NonEmptyStr = constr(min_length=1, strip_whitespace=True)


class HandleDocumentsRequest(BaseModel):
    document_ids: List[NonEmptyStr] = Field(..., min_length=1)


class HandleChunksRequest(BaseModel):
    chunks_ids: Optional[List[NonEmptyStr]] = Field([], min_length=1)
