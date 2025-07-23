from fastapi import FastAPI, Query, HTTPException
from fullbay import fetch_fullbay_data

app = FastAPI()

@app.get("/get-invoices")
def get_invoices(start: str = Query(...), end: str = Query(...)):
    try:
        endpoint = "https://app.fullbay.com/services/getInvoices.php"
        data = fetch_fullbay_data(endpoint, start, end)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
