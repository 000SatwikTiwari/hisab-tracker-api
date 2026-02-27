## uvicorn temp:app --reload

from fastapi import FastAPI, Path, HTTPException
from datetime import date
from typing import Annotated
from pymongo import MongoClient

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb+srv://db_sat:otXj03GNr05TcQHK@cluster0.iotuxte.mongodb.net/jobtracker?retryWrites=true&w=majority&appName=Cluster0")

db = client["jobtracker"]
collection = db["hisab_data"]



@app.post("/hisab/{name}/{amount}")
def save_data(
    name: str,
    amount: Annotated[float, Path(gt=0)],
    hisab_date: date | None = None
):
    data = {
        "Name": name,
        "Amount": amount,
        "hisab_date": str(hisab_date) if hisab_date else None
    }

    collection.insert_one(data)

    return {"message": "Added successfully"}



@app.get("/data/{name}")
def give_data(name: str):

    return_list = []
    total = 0

    records = collection.find({"Name": name})

    for x in records:
        return_list.append({
            "paid RS": x["Amount"],
            "On-Date": x.get("hisab_date")
        })
        total += x["Amount"]

    return {
        "Transactions": return_list,
        "Total_given": total
    }



@app.delete("/delete/{name}")
def delete_data(
    name: str,
    hisab_date: date
):
    delete_date = str(hisab_date)

    result = collection.delete_one({
        "Name": name,
        "hisab_date": delete_date
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": "Record deleted successfully"}

@app.get("/workers")
def get_unique_workers():

    # Get distinct names from MongoDB
    workers = collection.distinct("Name")

    return {
        "Total_workers": len(workers),
        "Workers": workers
    }
