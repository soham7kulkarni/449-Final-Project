# Importing all dependencies
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel 
from pymongo.mongo_client import MongoClient
import motor.motor_asyncio
from bson.objectid import ObjectId
from urllib.parse import quote



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
    title: Optional[str]
    authors: Optional[str]
    description: Optional[str] = None
    price: Optional[float]
    stock: Optional[float]




# creating instance of FastApi
app = FastAPI()

# ceating endpoints 
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/total")
async def total():
    count = await collection.count_documents({})
    return count

@app.get("/top5books")
async def top_5_books():
    top_books = await collection.aggregate([
        {"$group": {"_id": "$title", "total_stock": {"$sum": "$stock"}}},
        {"$sort": {"total_stock": -1}},
        {"$limit": 5}]).to_list(length=None)
    return top_books


@app.get("/top5authors")
async def top_5_authors():
    top_authors = await collection.aggregate([
        {"$group": {"_id": "$authors", "total_stock": {"$sum": "$stock"}}},
        {"$sort": {"total_stock": -1}},
        {"$limit": 5}]).to_list(length=None)
    return top_authors




@app.get("/bookss/{title}")
async def get_book_by_title(title: str):
    book = await collection.find_one({"title": str(title)})
    return Book(**book)

@app.get("/query/")
async def get_book_by_query(title: str = None, author: str = None, min_price: int = None, max_price: int = None):
    query = {}
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        if "price" in query:
            query["price"]["$lte"] = max_price
        else:
            query["price"] = {"$lte": max_price}
    if title is not None:
        query["title"] = {"$regex": title, "$options": "i"}
    if author is not None:
        query["authors"] = {"$regex": author, "$options": "i"}
    books = []
    async for book in collection.find(query):
        books.append(Book(**book))
    return books
    

# @app.get("/{title}")
# async def get_book_by_title(title: str):
#     # sample_list=[]
#     # for i in title:
#     #     if i.isalnum():
#     #         sample_list.append(i)
#     #     normal_string="".join(sample_list)
#     escaped_title = quote(title)
#     book = await collection.find_one({"title": str(escaped_title)})
#     if book is None:
#         return {"message": "Book with id {} not found".format(book_id)}
#     return Book(**book)

@app.get("/books/{book_id}")
async def get_book(book_id: str):
    print(book_id)
    book = await collection.find_one({"_id": ObjectId(book_id)})
    if book is None:
        return {"message": "Book with id {} not found".format(book_id)}
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

@app.put("/{id}")
async def update_book(id: str, book: Book):
    book_dict = book.dict()
    result = await collection.update_one({"_id": ObjectId(id)}, {"$set": book_dict})
    if result.modified_count == 1:
        return {"message": "Book with id {} updated".format(id)} 
    else:
        return {"message": "Book with id {} not found".format(id)}
