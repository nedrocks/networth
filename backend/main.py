from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Item, ItemList

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
items = [
    Item(id=1, name="Task 1", description="Complete the project", status="pending"),
    Item(id=2, name="Task 2", description="Review the code", status="completed"),
    Item(id=3, name="Task 3", description="Deploy to production", status="in_progress"),
]

@app.get("/api/items", response_model=ItemList)
async def get_items():
    return ItemList(items=items)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)