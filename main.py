# Importing all dependencies
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel 
from pymongo.mongo_client import MongoClient
import motor.motor_asyncio
from bson.objectid import ObjectId



# Asynchronous connection with MongoDB
uri = "mongodb+srv://root:CP107@cluster0.gospo3x.mongodb.net/?retryWrites=true&w=majority"
port = 8000
client = motor.motor_asyncio.AsyncIOMotorClient(uri, port = port)
db = client["db1"]
collection = db["collection"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)




# Customized Pydantic model for data validation 
class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    price: float
    stock: int



# creating instance of FastApi
app = FastAPI()

# ceating endpoints 
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/books/{book_id}")
async def get_book(book_id: str):
    book = await collection.find_one({"_id": ObjectId(book_id)})
    return Book(**book)

@app.get("/bookDetails")
async def get_all_books():
    books = []
    async for book in collection.find():
        books.append(Book(**book))
    return books

@app.post("/books")
async def add_book(book:Book):
    book_dict = book.dict()
    print(book_dict)
    result = await collection.insert_one(book_dict)
    inserted_book = await collection.find_one({"_id": result.inserted_id})
    return Book(**inserted_book)

@app.delete("/{id}")
async def delete_book(id: str):
    result = await collection.find_one({"_id": ObjectId(id)})
    if result:
        title = result['title']
        await collection.delete_one({"_id": ObjectId(id)})
        return {"message":f"book with title '{title}' deleted"}
    else:
        return {"message": f"Book with id '{id}' not found."}
 
# @app.put("/books/{book_id}")
# async def update_book():
#     return ___________

# @app.delete("/books/{book_id}")
# async def delete_book():
#     return ___________