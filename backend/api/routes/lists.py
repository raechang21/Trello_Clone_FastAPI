from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from typing import List
from models.card import CardSchema
from pydantic import BaseModel, ConfigDict, Field
from models.base import PyObjectId
import database

router = APIRouter()

# --- 定義 Payload Models ---
class CreateListPayload(BaseModel):
    name: str

class UpdateListPayload(BaseModel):
    name: str

class ListSimpleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    name: str

class ListDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PyObjectId = Field(validation_alias="_id", serialization_alias="id")
    name: str
    cards: List[CardSchema] # 包含完整的卡片資訊

# --- Routes & Controller Logic ---

# 1. Get all lists (對應 getLists)
# 只回傳 id 與 name
@router.get("/", response_model=List[ListSimpleResponse])
async def get_all_lists():
    cursor = database.db.lists.find({}, {"name": 1}) # 僅投射 name 欄位
    return await cursor.to_list(length=1000)

# 2. Get a list (對應 getList + .populate("cards"))
@router.get("/{id}", response_model=ListDetailResponse)
async def get_list(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # 使用 MongoDB Aggregation 模擬 Mongoose 的 populate 邏輯
    pipeline = [
        {"$match": {"_id": ObjectId(id)}},
        {
            "$lookup": {
                "from": "cards",           # 關聯的集合名稱
                "localField": "_id",       # List 的 id
                "foreignField": "list_id", # Card 裡指向 List 的欄位
                "as": "cards"              # 輸出的欄位名稱
            }
        }
    ]
    
    results = await database.db.lists.aggregate(pipeline).to_list(length=1)
    if not results:
        raise HTTPException(status_code=404, detail="id is not valid")
        
    return results[0]

# 3. Create a list (對應 createList)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_list(payload: CreateListPayload):
    new_list = {"name": payload.name, "cards": []}
    result = await database.db.lists.insert_one(new_list)
    return {"id": str(result.inserted_id)}

# 4. Update a list (對應 updateList)
@router.put("/{id}")
async def update_list_name(id: str, payload: UpdateListPayload):
    result = await database.db.lists.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"name": payload.name}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="id is not valid")
    return "OK"

# 5. Delete a list (去交易化版本)
@router.delete("/{id}")
async def delete_list_and_cards(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    deleted_list = await database.db.lists.find_one_and_delete(
        {"_id": ObjectId(id)}
    )
    
    if not deleted_list:
        raise HTTPException(status_code=404, detail="id is not valid")


    await database.db.cards.delete_many(
        {"list_id": ObjectId(id)}
    )
    
    return "OK"