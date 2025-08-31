from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client
import asyncio
import httpx
from typing import Optional, Dict, List


def get_sequence_active():
    resp = supabase_client.table('sequences').select('name').eq('active', True).single().execute()
    return resp.data['name']


def get_quarter_active():
    resp = supabase_client.table('quarters').select('name').eq('active', True).single().execute()
    return resp.data['name']


def get_current_year_label():
    resp = supabase_client.table('years').select('name').eq('active', True).single().execute()
    return resp.data['name']


def get_current_year_short():
    resp = supabase_client.table('years').select('short').eq('active', True).single().execute()
    return resp.data['short']


def get_current_year_id():
    resp = supabase_client.table('years').select('id').eq('active', True).single().execute()
    return resp.data['id']


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


async def get_active_sequence(access_token: str) -> Optional[Dict]:
    """
    Récupère la séquence active dans la table 'sequences'.
    Retourne un dictionnaire avec tous les champs ou None si aucune active.
    """
    request_url = f"{url}/rest/v1/sequences?select=*&active=eq.true&limit=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None


async def get_active_quarter(access_token: str) -> str | None:
    """
        Récupère le trimestre actif dans la table 'quarters'.
        Retourne un dictionnaire avec tous les champs ou None si aucune active.
        """
    request_url = f"{url}/rest/v1/quarters?select=*&active=eq.true&limit=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None







