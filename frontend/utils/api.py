import requests

BASE_URL = "http://127.0.0.1:8000/api"

def list_databases():
    r = requests.get(f"{BASE_URL}/")
    try:
        return r.json()
    except Exception:
        print("Response text:", r.text)
    return {}


def list_tables(db_name):
    r = requests.get(f"{BASE_URL}/{db_name}")
    return r.json()

def upload_file(file_path, table_name=None, db_name=None, if_exists="replace"):
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        data = {"table_name": table_name, "if_exists": if_exists, "db_name": db_name}
        r = requests.post(f"{BASE_URL}/upload/", files=files, data=data)
    return r.json()

def nl_to_sql(question, db_name):
    r = requests.post(f"{BASE_URL}/nl2sql/", json={"question": question, "db_name": db_name})
    return r.json()

def execute_sql(sql_query, db_name):
    r = requests.post(f"{BASE_URL}/execute/", json={"sql_query": sql_query, "db_name": db_name})
    return r.json()
