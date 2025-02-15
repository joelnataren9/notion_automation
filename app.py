from flask import Flask, request
import requests
import json
import os
import datetime
app = Flask(__name__)



NOTION_SECRET_TOKEN = os.getenv("NOTION_SECRET_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")


headers = {
    "Authorization": f"Bearer {NOTION_SECRET_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "page_size": 100
    }
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    with open("db_notion.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    results = data["results"]
    return results


@app.route("/", methods=["GET", "POST"])
def home():
    return "Hello World"

@app.route("/add_expense_entry", methods=["POST"])
def add_expense_entry():
    expense = request.form.get("Expense", None)
    amount = request.form.get("Amount", None)
    category = request.form.get("Category", None)
    comment = request.form.get("Comment", None)

    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {
            "database_id": DATABASE_ID
        },
        "properties": {}
    }
    if expense:
        payload["properties"]["Expense"] = {
            "title": [
                {
                    "text": {
                        "content": expense
                    }
                }
            ]
        }
    if amount:
        payload["properties"]["Amount"] = {
            "number": float(amount)
        }
    if category:
        payload["properties"]["Category"] = {
            "multi_select": [
                {
                    "name": category
                }
            ]
        }
    if comment:
        payload["properties"]["Comment"] = {
            "rich_text": [
                {
                    "text": {
                        "content": comment
                    }
                }
            ]
        }
    if not expense or not amount or not category:
        return {"message": "Please provide all the required fields"}, 400
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print(data)

    return {"message": "Success"}, 200

# Get all expenses for current month 
@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    pages = get_pages()
    expenses = []
    for page in pages:
        properties = page["properties"]
        date = properties["Date"]["date"]["start"]

        current_month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        print(date, current_month, year)

        print(properties, end="\n\n")
        try:
            expense = properties["Expense"]["title"][0]["text"]["content"]
        except:
            expense = None
        try:
            amount = properties["Amount"]["number"]
        except:
            amount = None
        try:
            category = properties["Category"]["multi_select"][0]["name"]
        except:
            category = None
        try:
            comment = properties["Comment"]["rich_text"][0]["text"]["content"]
        except:
            comment = None

        # Add the expense if it is from the current month
        expense_month = int(date.split("-")[1])
        expense_year = int(date.split("-")[0])
        if expense_month == current_month and expense_year == year:
            expenses.append({
            "Expense": expense,
            "Amount": amount,
            "Category": category,
            "Comment": comment,
            "Date": date
            })
    return {"expenses": expenses}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0")

# from app import app
