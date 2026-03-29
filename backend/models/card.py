from datetime import datetime
from typing import Optional
from .base import MongoBaseModel, PyObjectId
from pydantic import AliasChoices, Field

class CardSchema(MongoBaseModel):
    # 對應 Mongoose 的 transform 邏輯：將 _id 映射為 id
    id: Optional[PyObjectId] = Field(
        validation_alias="_id",
        serialization_alias="id",
        default=None,
    )
    title: str = Field(..., description="Card title is required")
    description: str = Field(..., description="Description is required")
    
    # 對應 ref: "List"
    list_id: PyObjectId = Field(...)

    # Mongoose timestamps: true 預設為 createdAt / updatedAt
    created_at: datetime = Field(
        default_factory=datetime.now,
        validation_alias=AliasChoices("created_at", "createdAt"),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        validation_alias=AliasChoices("updated_at", "updatedAt"),
    )