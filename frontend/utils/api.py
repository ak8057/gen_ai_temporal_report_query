import requests

BASE_URL = "http://127.0.0.1:8000/api"

def upload_file(file_path, table_name=None, if_exists="replace"):
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        data = {"table_name": table_name, "if_exists": if_exists}
        r = requests.post(f"{BASE_URL}/upload/", files=files, data=data)
    return r.json()

def nl_to_sql(question):
    r = requests.post(f"{BASE_URL}/nl2sql/", json={"question": question})
    return r.json()

def execute_sql(sql_query):
    r = requests.post(f"{BASE_URL}/execute/", json={"sql_query": sql_query})
    return r.json()
