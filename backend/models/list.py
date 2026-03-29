from datetime import datetime
from typing import List, Optional
from .base import MongoBaseModel, PyObjectId
from pydantic import Field

class ListSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(
        validation_alias="_id",
        serialization_alias="id",
        default=None,
    )
    name: str = Field(..., description="List name is required")
    
    # 對應 cards: [{ type: ObjectId, ref: 'Card' }]
    cards: List[PyObjectId] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)