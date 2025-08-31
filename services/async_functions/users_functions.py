from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client, app_url
import asyncio
import httpx
from typing import List, Dict
from collections import Counter


async def get_active_year_id(access_token) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/years?active=eq.true&select=id",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
        )
        data = response.json()
        return data[0]['id'] if data else None


async def get_all_users(access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/users",
            headers=headers,
            params={"select": "*"}  # Sélectionne toutes les colonnes
        )

        if res.status_code == 200:
            return res.json()
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return []
