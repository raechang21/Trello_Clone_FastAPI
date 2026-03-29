# 檔案路徑：main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import cards, lists
from utils.config import settings
import database  # 導入剛剛建立的資料庫模組

app = FastAPI(title="Task Management API")

# 前端 dev server（Vite）與 Node 後端慣用來源；allow_credentials=False 與 axios 預設一致，
# 且避免與 allow_origins=["*"] 在部分瀏覽器下的組合問題。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router, prefix="/api/cards", tags=["Cards"])
app.include_router(lists.router, prefix="/api/lists", tags=["Lists"])

@app.on_event("startup")
async def startup_event():
    # 呼叫 database.py 的連線邏輯
    await database.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await database.close_mongo_connection()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)