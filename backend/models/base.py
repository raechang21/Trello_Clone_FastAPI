from typing import Annotated, Any
from pydantic import BeforeValidator, ConfigDict, BaseModel, Field

# 將 MongoDB 的 ObjectId 轉換為字串的邏輯處理
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,      # 允許使用 id 或 _id 賦值
        serialization_alias_only=False, # 確保序列化時邏輯正確
        from_attributes=True        # 允許從物件屬性讀取
    )