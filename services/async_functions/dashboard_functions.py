from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key
import asyncio
import httpx
from typing import Optional, Dict, List


async def get_dashboard_stats(access_token: str, year_id: str):
    """

    :param access_token:
    :param year_id:
    :return:
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    query_url = (
        f"{url}/rest/v1/dashboard_school_stats"
    )
    params = {
        "select": "*",
        "year_id": f"eq.{year_id}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(query_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    return data
