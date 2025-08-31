from postgrest import AsyncPostgrestClient
from services.supabase_client import *
import asyncio
import httpx
from typing import List, Dict
import random

# HEADERS = {"apikey": key, "Authorization": f"Bearer {key}"}
SCHOOL_CODE = 'LBA'

def get_current_year_label():
    resp = supabase_client.table('years').select('name').eq('active', True).single().execute()
    return resp.data['name']


def get_current_year_short():
    resp = supabase_client.table('years').select('short').eq('active', True).single().execute()
    return resp.data['short']



def get_current_year_id():
    resp = supabase_client.table('years').select('id').eq('active', True).single().execute()
    return resp.data['id']


def get_new_registration_number():
    return f"{school_code}{random.randint(1000, 9999)}"


def get_amount_paid_by_student_id(student_id):
    resp = supabase_client.table('school_fees').select('amount').eq(
        'student_id', student_id
    ).eq('year_id', get_current_year_id()).execute()

    amount = 0
    if resp.data:
        for row in resp.data:
            amount += row['amount']

    return amount


def get_all_payments_by_student(student_id):
    resp = supabase_client.table('school_fees').select('*').eq(
        'student_id', student_id
    ).eq('year_id', get_current_year_id()).execute()

    return resp.data


def total_school_fees():
    resp = (supabase_client.table('fees_part').select('amount').eq(
        'year_id', get_current_year_id()).neq('part', 'inscription').execute())

    amount = 0
    if resp.data:
        for row in resp.data:
            amount += row['amount']

    return amount


def get_student_name_by_id(student_id):
    resp = supabase_client.table('students').select('*').eq('id', student_id).single().execute()
    return f"{resp.data['name']} {resp.data['surname']}"

# async functions...
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


async def get_students_with_details(page_number: int, access_token: str, year_id: str) -> List[dict]:
    """
    :param page_number:
    :param access_token:
    :param year_id:
    :return:
    """
    decalage = page_number * 100
    query_url = f"{url}/rest/v1/registrations_view"
    params = {
        "select": "*",
        "limit": 100,
        "offset": decalage,
        "year_id": f"eq.{year_id}"
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(query_url, headers=headers, params=params)

        if response.status_code != 200:
            print("Erreur :", response.text)
            return []

        return response.json()


async def get_students_with_details_wf(access_token: str, year_id: str,) -> List[dict]:
    """

    :param page_number:
    :param access_token:
    :param year_id:
    :return:
    """

    query_url = f"{url}/rest/v1/registrations_view"
    params = {
        "select": "*",
        "limit": 5000,
        "year_id": f"eq.{year_id}",
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(query_url, headers=headers, params=params)

        if response.status_code != 200:
            print("Erreur :", response.text)
            return []

        return response.json()


async def get_unregistered_students(access_token: str) -> List[dict]:
    query_url = f"{url}/rest/v1/students_not_registered_active_year"
    params = {
        "select": "*",
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(query_url, headers=headers, params=params)

        if response.status_code != 200:
            print("Erreur :", response.text)
            return []

        return response.json()


async def get_active_classes(access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes?active=eq.true&select=id,code",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        data = response.json()
        return data


async def get_fees_amount_by_year(access_token: str, year_id: str) -> Dict:
    """

    :param access_token:
    :param year_id:
    :return:
    """
    query_url = f"{url}/rest/v1/vw_fees_by_type_pivot"
    params={
        "select": "*",
        "year_id": f"eq.{year_id}",
    }
    headers={
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            query_url,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]
        return None


async def get_class_code_by_id_async(class_id: str, access_token: str) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes",
            params={
                "select": "code",
                "id": f"eq.{class_id}",
                "limit": 1
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0].get("code")
        return None


async def get_student_payments_for_active_year(access_token: str, student_id: str, year_id: str) -> List[dict]:
    """

    :param access_token:
    :param student_id:
    :param year_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/school_fees",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "part,amount,date",
                "year_id": f"eq.{year_id}",
                "student_id": f"eq.{student_id}",
                "order": "date.desc"
            }
        )
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return []


async def get_total_school_fees_for_active_year(access_token: str) -> int:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return 0

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/fees_part",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "amount",
                "year_id": f"eq.{year_id}",
                "part": "not.eq.inscription"
            }
        )
        if res.status_code == 200:
            data = res.json()
            total = sum(item["amount"] for item in data)
            return total
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return 0


async def get_all_classes_basic_info(access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    url_request = (
        f"{url}/rest/v1/classes"
        f"?select=id,code,level_id"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_request, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data  # Liste de dictionnaires avec id, code, level_id


async def get_registered_students(access_token: str, year_id: str) -> List[dict]:
    """
    Retourne les id, name, surname des élèves inscrits pour une année donnée.
    """
    request_url = (
        f"{url}/rest/v1/students"
        f"?select=id,name,surname,registrations!inner(year_id)"
        f"&registrations.year_id=eq.{year_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        return response.json()


async def insert_discipline_entry(access_token: str, data: dict) -> dict:
    """
    Insère une ligne dans la table 'discipline' à partir d’un dictionnaire de données.
    Le dictionnaire 'data' doit contenir les clés : year_id, student_id, type, quantity.
    """
    query_url = f"{url}/rest/v1/discipline"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            query_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=data
        )
        response.raise_for_status()
        return response.json()[0]


async def get_student_discipline_active_sequence(access_token: str, student_id: str, year_id: str, sequence: str) -> List[dict]:
    """

    :param access_token:
    :param student_id:
    :param year_id:
    :param sequence:
    :return:
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/discipline",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "*",
                "year_id": f"eq.{year_id}",
                "student_id": f"eq.{student_id}",
                "sequence": f"eq.{sequence}"
            }
        )
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return []





