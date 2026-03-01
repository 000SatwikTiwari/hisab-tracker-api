from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
from datetime import date
from typing import Annotated
from pymongo import MongoClient
## uvicorn temp1:app --reload


app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb+srv://db_sat:otXj03GNr05TcQHK@cluster0.iotuxte.mongodb.net/jobtracker?retryWrites=true&w=majority&appName=Cluster0")

db = client["jobtracker"]
collection = db["hisab_data"]


# =========================
# FRONTEND ROUTE
# =========================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Hisab Tracker Pro</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', sans-serif;
}

body {
    background: linear-gradient(135deg, #667eea, #764ba2);
    min-height: 100vh;
    padding: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

h1 {
    color: white;
    margin-bottom: 30px;
    font-size: 32px;
    letter-spacing: 1px;
}

.container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    width: 100%;
    max-width: 1100px;
}

.card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    color: white;
}

.card h2 {
    margin-bottom: 15px;
}

input {
    width: 100%;
    padding: 10px;
    margin: 6px 0;
    border: none;
    border-radius: 8px;
}

button {
    width: 100%;
    padding: 10px;
    margin-top: 8px;
    border: none;
    border-radius: 8px;
    background: #ff7eb3;
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: 0.3s ease;
}

button:hover {
    background: #ff4f91;
    transform: translateY(-2px);
}

table {
    width: 100%;
    margin-top: 10px;
    border-collapse: collapse;
    background: rgba(255,255,255,0.2);
    border-radius: 8px;
    overflow: hidden;
}

th, td {
    padding: 8px;
    text-align: center;
}

th {
    background: rgba(0,0,0,0.2);
}

#total {
    margin-top: 10px;
    font-weight: bold;
}

ul {
    margin-top: 10px;
}

li {
    padding: 5px 0;
}
</style>
</head>
<body>

<h1>💰 Hisab Tracker Dashboard - By Satwik</h1>

<div class="container">

<div class="card">
<h2>Add Entry</h2>
<input type="text" id="addName" placeholder="Name">
<input type="number" id="addAmount" placeholder="Amount">
<input type="date" id="addDate">
<button onclick="addEntry()">Add Entry</button>
</div>

<div class="card">
<h2>View Transactions</h2>
<input type="text" id="getName" placeholder="Name">
<button onclick="getData()">Fetch Data</button>
<h3 id="total"></h3>
<table>
<thead>
<tr><th>Amount</th><th>Date</th></tr>
</thead>
<tbody id="dataTable"></tbody>
</table>
</div>

<div class="card">
<h2>Delete Entry</h2>
<input type="text" id="deleteName" placeholder="Name">
<input type="date" id="deleteDate">
<button onclick="deleteEntry()">Delete Entry</button>
</div>

<div class="card">
<h2>Workers</h2>
<button onclick="getWorkers()">Show Workers</button>
<ul id="workersList"></ul>
</div>

</div>

<script>
async function addEntry() {
    const name = document.getElementById("addName").value;
    const amount = document.getElementById("addAmount").value;
    const date = document.getElementById("addDate").value;

    let url = `/hisab/${name}/${amount}`;
    if (date) url += `?hisab_date=${date}`;

    const res = await fetch(url, { method: "POST" });
    const data = await res.json();
    alert(data.message);
}

async function getData() {
    const name = document.getElementById("getName").value;
    const res = await fetch(`/data/${name}`);
    const data = await res.json();

    const table = document.getElementById("dataTable");
    table.innerHTML = "";

    data.Transactions.forEach(item => {
        table.innerHTML += `
        <tr>
            <td>${item["paid RS"]}</td>
            <td>${item["On-Date"] || "-"}</td>
        </tr>`;
    });

    document.getElementById("total").innerText =
        "Total Given: ₹ " + data.Total_given;
}

async function deleteEntry() {
    const name = document.getElementById("deleteName").value;
    const date = document.getElementById("deleteDate").value;

    const res = await fetch(`/delete/${name}?hisab_date=${date}`, {
        method: "DELETE"
    });

    const data = await res.json();
    alert(data.message);
}

async function getWorkers() {
    const res = await fetch(`/workers`);
    const data = await res.json();

    const list = document.getElementById("workersList");
    list.innerHTML = "";

    data.Workers.forEach(worker => {
        list.innerHTML += `<li>${worker}</li>`;
    });
}
</script>

</body>
</html>
"""

# =========================
# API ROUTES
# =========================

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
def delete_data(name: str, hisab_date: date):
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
    workers = collection.distinct("Name")

    return {
        "Total_workers": len(workers),
        "Workers": workers
    }
