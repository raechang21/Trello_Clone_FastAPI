from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from typing import List
from models.card import CardSchema
from pydantic import BaseModel
import database

router = APIRouter()

# --- 定義 Payload Models (取代原有的 TypeScript Interfaces) ---
class CreateCardPayload(BaseModel):
    title: str
    description: str
    list_id: str

class UpdateCardPayload(BaseModel):
    title: str | None = None
    description: str | None = None
    list_id: str | None = None

# --- Routes & Controller Logic ---

# 1. Get all cards (對應 getCards)
@router.get("/", response_model=List[CardSchema])
async def get_cards():
    cursor = database.db.cards.find({})
    return await cursor.to_list(length=1000)

# 2. Get a card (對應 getCard)
@router.get("/{id}", response_model=CardSchema)
async def get_card(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    card = await database.db.cards.find_one({"_id": ObjectId(id)})
    if not card:
        raise HTTPException(status_code=404, detail="id is not valid")
    return card


# 3. Create a card (你剛才提供的邏輯)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_card(payload: CreateCardPayload):
    # 檢查目標 List 是否存在
    list_exists = await database.db.lists.find_one({"_id": ObjectId(payload.list_id)})
    if not list_exists:
        raise HTTPException(status_code=404, detail="list_id is not valid")

    new_card = {
        "title": payload.title,
        "description": payload.description,
        "list_id": ObjectId(payload.list_id)
    }
    result = await database.db.cards.insert_one(new_card)
    
    # 同步更新 List 中的 cards 陣列
    await database.db.lists.update_one(
        {"_id": ObjectId(payload.list_id)},
        {"$push": {"cards": result.inserted_id}}
    )
    return {"id": str(result.inserted_id)}

# 4. Update a card (移除 Transaction)
@router.put("/{id}")
async def update_card(id: str, payload: UpdateCardPayload):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # 1. 確認卡片是否存在
    old_card = await database.db.cards.find_one({"_id": ObjectId(id)})
    if not old_card:
        raise HTTPException(status_code=404, detail="id is not valid")

    update_data = payload.model_dump(exclude_unset=True)
    
    # 2. 如果涉及跨 List 移動
    if "list_id" in update_data:
        new_list_id = ObjectId(update_data["list_id"])
        if not await database.db.lists.find_one({"_id": new_list_id}):
            raise HTTPException(status_code=404, detail="list_id is not valid")
        
        # 從舊 List 移除
        await database.db.lists.update_one(
            {"_id": old_card["list_id"]}, 
            {"$pull": {"cards": ObjectId(id)}}
        )
        # 加入新 List
        await database.db.lists.update_one(
            {"_id": new_list_id}, 
            {"$push": {"cards": ObjectId(id)}}
        )
        update_data["list_id"] = new_list_id

    # 3. 執行卡片本身的更新
    await database.db.cards.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return "OK"

# 5. Delete a card (移除 Transaction)
@router.delete("/{id}")
async def delete_card(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # 1. 刪除卡片並取得其資料以獲得 list_id
    deleted_card = await database.db.cards.find_one_and_delete({"_id": ObjectId(id)})
    if not deleted_card:
        raise HTTPException(status_code=404, detail="id is not valid")

    # 2. 從對應的 List 中移除該卡片引用
    await database.db.lists.update_one(
        {"_id": deleted_card["list_id"]},
        {"$pull": {"cards": ObjectId(id)}}
    )
    return "OK"