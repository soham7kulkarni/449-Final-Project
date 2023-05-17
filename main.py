# Importing all dependencies
import uvicorn
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
    book_id:int
    title: str
    author: Optional[str]
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
async def get_book(book_id: int):
    book = await collection.find_one({"book_id":book_id})
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

@app.put("/books/{book_id}")
async def update_book(book_id:int,book:Book):
    result = await collection.find_one({"book_id":book_id})
    if result:
        updated_result=await collection.replace_one({"book_id":book_id},{"book_id":book_id,"title":book.title,"author":book.author,"description":book.description,"price":book.price,"stock":book.stock})
        return {"message":f"total {updated_result.modified_count} books changed"}
    else:
        return "book with id : {book_id} not found"

@app.delete("/{id}")
async def delete_book(id: int):
    result = await collection.find_one({"book_id": id})
    if result:
        title = result['title']
        await collection.delete_one({"book_id": id})
        return {"message":f"book with title '{title}' deleted"}
    else:
        return {"message": f"Book with id '{id}' not found."}

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
 
# @app.put("/books/{book_id}")
# async def update_book():
#     return ___________

# @app.delete("/books/{book_id}")
# async def delete_book():
#     return ___________