## hellodharti_enum.py
##uvicorn hellodharti_enum:app --reload
## Enum set krta hai ki ham kewal predefine values hi use krein , like labours me kewal registered user hi aainn
## yaha ham date ko optional banaenge
from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum
from typing import Annotated
from fastapi import Query

from fastapi import FastAPI

app = FastAPI()

hisab_list = []

# ✅ Enum for Name
class NameEnum(str, Enum):
    satwik = "Satwik"
    rahul = "Rahul"
    aman = "Aman"

@app.post("/hisab/{Name}/{Ammount}")
def save_data(Name: NameEnum, Ammount: Annotated[float,Path(gt=0, lt=1000)], hisab_date: date | None =None):  ##where we were defining data type we added our class
                                                                                        ## and date is optional
                                                                                        ## using annotated 
    hisab_list.append({"Name": Name, "Amount": Ammount, "hisab_date": hisab_date}) 
    
    return {"message": "Added successfully"}

@app.get("/data/{Name}")
def give_data(Name: NameEnum):
    for x in hisab_list:
        if x["Name"] == Name:
            return {"paid RS":x["Amount"], "Till-Date":x["hisab_date"]}