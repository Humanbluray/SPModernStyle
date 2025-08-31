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


async def get_global_students_fees_status(access_token: str) -> list[dict]:
    year_id = await get_active_year_id(access_token)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    # Étape 1 : Total des frais de scolarité attendus (hors inscription)
    async with httpx.AsyncClient() as client:
        expected_total = await get_total_school_fees_for_active_year(access_token)

    # Étape 2 : Récupérer tous les élèves inscrits pour cette année
    async with httpx.AsyncClient() as client:
        students_res = await client.get(
            f"{url}/rest/v1/registrations",
            headers=headers,
            params={
                "select": "student_id,class_id,students(name,surname),classes(code)",
                "year_id": f"eq.{year_id}"
            }
        )
        if students_res.status_code != 200:
            print("Erreur étudiants:", students_res.text)
            return []

        registrations = students_res.json()

    results = []

    # Étape 3 : Pour chaque élève, calculer les paiements
    async with httpx.AsyncClient() as client:
        for reg in registrations:
            student_id = reg["student_id"]
            student_name = reg.get("students", {}).get("name")
            student_surname = reg.get("students", {}).get("surname")
            class_id = reg.get("class_id")
            class_code = reg.get("classes", {}).get("code")

            fees_res = await client.get(
                f"{url}/rest/v1/school_fees",
                headers=headers,
                params={
                    "select": "amount",
                    "student_id": f"eq.{student_id}",
                    "year_id": f"eq.{year_id}",
                    "part": "not.eq.inscription"
                }
            )
            if fees_res.status_code != 200:
                print(f"Erreur fees for student {student_id}: {fees_res.text}")
                continue

            paid_total = sum(item["amount"] for item in fees_res.json())
            status = True if paid_total == expected_total else False

            results.append({
                "id": student_id,
                "name": student_name,
                "surname": student_surname,
                "class id": class_id,
                "class code": class_code,
                "total_paid": paid_total,
                'total expected': expected_total,
                'total stayed': expected_total - paid_total,
                "status": status
            })

    return results


async def get_global_students_fees_status_by_class(access_token: str, class_id: str) -> list[dict]:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    # Étape 1 : Total des frais attendus (hors inscription)
    async with httpx.AsyncClient() as client:
        fees_res = await client.get(
            f"{url}/rest/v1/fees_part",
            headers=headers,
            params={
                "select": "amount",
                "year_id": f"eq.{year_id}",
                "part": "not.eq.inscription"
            }
        )
        if fees_res.status_code != 200:
            print("Erreur total attendu:", fees_res.text)
            return []

        expected_total = sum(item["amount"] for item in fees_res.json())

    # Étape 2 : Élèves inscrits dans la classe spécifiée pour l’année active
    async with httpx.AsyncClient() as client:
        students_res = await client.get(
            f"{url}/rest/v1/registrations",
            headers=headers,
            params={
                "select": "student_id,students(name,surname),classes(code)",
                "year_id": f"eq.{year_id}",
                "class_id": f"eq.{class_id}"
            }
        )
        if students_res.status_code != 200:
            print("Erreur étudiants:", students_res.text)
            return []

        registrations = students_res.json()

    results = []

    # Étape 3 : Paiements pour chaque élève
    async with httpx.AsyncClient() as client:
        for reg in registrations:
            student_id = reg["student_id"]
            student_name = reg.get("students", {}).get("name")
            student_surname = reg.get("students", {}).get("surname")
            class_code = reg.get("classes", {}).get("code")

            fees_res = await client.get(
                f"{url}/rest/v1/school_fees",
                headers=headers,
                params={
                    "select": "amount",
                    "student_id": f"eq.{student_id}",
                    "year_id": f"eq.{year_id}",
                    "part": "not.eq.inscription"
                }
            )
            if fees_res.status_code != 200:
                print(f"Erreur fees pour l'élève {student_id}: {fees_res.text}")
                continue

            paid_total = sum(item["amount"] for item in fees_res.json())
            status = True if paid_total == expected_total else False

            results.append({
                "id": student_id,
                "name": student_name,
                "surname": student_surname,
                "class id": class_id,
                "class code": class_code,
                "total_paid": paid_total,
                'total expected': expected_total,
                'total stayed': expected_total - paid_total,
                "status": status
            })

    return results


# par tranche...
async def get_students_fees_status_by_part(access_token: str, part_name: str) -> list[dict]:
    year_id = await get_active_year_id(access_token)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    # Étape 1 : Montant attendu pour cette tranche
    async with httpx.AsyncClient() as client:
        fees_res = await client.get(
            f"{url}/rest/v1/fees_part",
            headers=headers,
            params={
                "select": "amount",
                "year_id": f"eq.{year_id}",
                "part": f"eq.{part_name}"
            }
        )
        if fees_res.status_code != 200:
            print("Erreur montant attendu:", fees_res.text)
            return []

        expected_part_total = sum(item["amount"] for item in fees_res.json())

    # Étape 2 : Récupérer tous les élèves inscrits pour cette année
    async with httpx.AsyncClient() as client:
        students_res = await client.get(
            f"{url}/rest/v1/registrations",
            headers=headers,
            params={
                "select": "student_id,class_id,students(name,surname),classes(code)",
                "year_id": f"eq.{year_id}"
            }
        )
        if students_res.status_code != 200:
            print("Erreur étudiants:", students_res.text)
            return []

        registrations = students_res.json()

    results = []

    # Étape 3 : Pour chaque élève, récupérer les paiements pour cette tranche
    async with httpx.AsyncClient() as client:
        for reg in registrations:
            student_id = reg["student_id"]
            student_name = reg.get("students", {}).get("name")
            student_surname = reg.get("students", {}).get("surname")
            class_id = reg.get("class_id")
            class_code = reg.get("classes", {}).get("code")

            fees_res = await client.get(
                f"{url}/rest/v1/school_fees",
                headers=headers,
                params={
                    "select": "amount",
                    "student_id": f"eq.{student_id}",
                    "year_id": f"eq.{year_id}",
                    "part": f"eq.{part_name}"
                }
            )
            if fees_res.status_code != 200:
                print(f"Erreur fees pour élève {student_id}: {fees_res.text}")
                continue

            paid_total = sum(item["amount"] for item in fees_res.json())
            status = True if paid_total == expected_part_total else False

            results.append({
                "id": student_id,
                "name": student_name,
                "surname": student_surname,
                "class id": class_id,
                "class code": class_code,
                "total_paid": paid_total,
                'total expected': expected_part_total,
                'total stayed': expected_part_total - paid_total,
                "status": status
            })

    return results


async def get_students_fees_status_for_part_and_class(
    access_token: str,
    fees_part: str,
    class_id: str
) -> list[dict]:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    # Étape 1 : Montant attendu pour cette tranche (hors inscription)
    async with httpx.AsyncClient() as client:
        fees_res = await client.get(
            f"{url}/rest/v1/fees_part",
            headers=headers,
            params={
                "select": "amount",
                "year_id": f"eq.{year_id}",
                "part": f"eq.{fees_part}"
            }
        )
        if fees_res.status_code != 200:
            print("Erreur total attendu:", fees_res.text)
            return []

        expected_total = sum(item["amount"] for item in fees_res.json())

    # Étape 2 : Récupérer les élèves inscrits dans la classe donnée pour cette année
    async with httpx.AsyncClient() as client:
        students_res = await client.get(
            f"{url}/rest/v1/registrations",
            headers=headers,
            params={
                "select": "student_id,class_id,students(name,surname),classes(code)",
                "year_id": f"eq.{year_id}",
                "class_id": f"eq.{class_id}"
            }
        )
        if students_res.status_code != 200:
            print("Erreur étudiants:", students_res.text)
            return []

        registrations = students_res.json()

    results = []

    # Étape 3 : Paiement par élève pour cette tranche
    async with httpx.AsyncClient() as client:
        for reg in registrations:
            student_id = reg["student_id"]
            student_name = reg.get("students", {}).get("name")
            student_surname = reg.get("students", {}).get("surname")
            class_code = reg.get("classes", {}).get("code")

            fees_res = await client.get(
                f"{url}/rest/v1/school_fees",
                headers=headers,
                params={
                    "select": "amount",
                    "student_id": f"eq.{student_id}",
                    "year_id": f"eq.{year_id}",
                    "part": f"eq.{fees_part}"
                }
            )
            if fees_res.status_code != 200:
                print(f"Erreur fees for student {student_id}: {fees_res.text}")
                continue

            paid_total = sum(item["amount"] for item in fees_res.json())
            status = True if paid_total == expected_total else False

            results.append({
                "id": student_id,
                "name": student_name,
                "surname": student_surname,
                "class id": class_id,
                "class code": class_code,
                "total_paid": paid_total,
                'total expected': expected_total,
                'total stayed': expected_total - paid_total,
                "status": status
            })

    return results


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



async def get_student_fees_summary(access_token: str, year_id: str):
    """
    Récupère toutes les informations de la vue student_fees_summary
    :param access_token: token RLS
    :param year_id : année active
    :return: liste de dictionnaires (un par élève et année)
    """
    query_url = f"{url}/rest/v1/student_fees_summary"
    params = {
        "select": "*",
        "year_id": f"eq.{year_id}"
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url=query_url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()  # retourne tous les enregistrements
        else:
            raise Exception(f"Erreur {response.status_code}: {response.text}")


async def get_student_fees_summary_by_part(access_token:str, fees_part: str, year_id: int):
    """

    :param access_token:
    :param fees_part:
    :param year_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        query_url = f"{url}/rest/v1/student_fees_summary_by_part"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "select": "*",
            "fees_part": f"eq.{fees_part}",
            "year_id": f"eq.{year_id}"
        }
        r = await client.get(query_url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()








