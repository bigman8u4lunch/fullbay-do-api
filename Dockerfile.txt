# Use official Python base image
FROM python:3.10-slim

# Set workdir and copy requirements
WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
import os
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
import httpx
import openai

# Load environment variables
load_dotenv()  # expects FULLBAY_API_KEY, OPENAI_API_KEY

FULLBAY_API_KEY = os.getenv("FULLBAY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not (FULLBAY_API_KEY and OPENAI_API_KEY):
    raise RuntimeError(
        "Missing one or more required environment variables: FULLBAY_API_KEY, OPENAI_API_KEY"
    )

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

app = FastAPI()
http_client = httpx.AsyncClient(timeout=10.0)


class FullbayClient:
    BASE_URL = "https://app.fullbay.com/services"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._ip: Optional[str] = None
        self._token: Optional[str] = None
        self._token_date: Optional[str] = None

    async def _refresh_token(self) -> None:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if self._token_date != today or not self._token:
            try:
                resp = await http_client.get("https://api.ipify.org?format=text")
                resp.raise_for_status()
                self._ip = resp.text.strip()
            except httpx.RequestError as e:
                raise RuntimeError(f"Failed to fetch public IP: {e}")
            raw = f"{self.api_key}{today}{self._ip}"
            self._token = hashlib.sha1(raw.encode()).hexdigest()
            self._token_date = today

    async def _fetch(self, endpoint: str, params: dict) -> dict:
        await self._refresh_token()
        full_params = {"key": self.api_key, "token": self._token, **params}
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            resp = await http_client.get(url, params=full_params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Fullbay API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Network error contacting Fullbay API: {e}"
            )

    async def get_adjustments(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getAdjustments.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_counter_sales(
        self,
        start_date: str,
        end_date: str,
        customer_unit_id: Optional[int] = None,
        customer_title: Optional[str] = None,
        unit_number: Optional[str] = None,
        unit_nickname: Optional[str] = None,
        unit_identifier: Optional[str] = None,
        license_plate: Optional[str] = None,
    ) -> dict:
        params = {"startDate": start_date, "endDate": end_date}
        if customer_unit_id:
            params["customerUnitId"] = customer_unit_id
        elif customer_title:
            params["customerTitle"] = customer_title
            if unit_number:    params["unitNumber"]    = unit_number
            if unit_nickname:  params["unitNickname"]  = unit_nickname
            if unit_identifier:params["unitIdentifier"]= unit_identifier
            if license_plate:  params["licensePlate"]  = license_plate
        return await self._fetch("getCounterSales.php", params)

    async def get_customer_credits(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getCustomerCredits.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_customer_payments(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getCustomerPayments.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_invoices(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getInvoices.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_vendor_bills(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getVendorBills.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_vendor_credits(self, start_date: str, end_date: str) -> dict:
        return await self._fetch(
            "getVendorCredits.php",
            {"startDate": start_date, "endDate": end_date}
        )

    async def get_customer_unit(
        self,
        customer_unit_id: Optional[int] = None,
        customer_title: Optional[str] = None,
        unit_number: Optional[str] = None,
        unit_nickname: Optional[str] = None,
        unit_identifier: Optional[str]_

# Expose port (App Platform uses $PORT)
ENV PORT 8080
EXPOSE $PORT

# Start Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
