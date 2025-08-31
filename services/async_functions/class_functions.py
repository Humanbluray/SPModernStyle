from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client
import asyncio
import httpx
from typing import List, Optional, Dict
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


async def get_all_student_counts_by_class(access_token: str) -> dict:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return {}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/registrations",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "class_id",
                "year_id": f"eq.{year_id}"
            }
        )

        if res.status_code != 200:
            print(f"Erreur: {res.status_code}: {res.text}")
            return {}

        data = res.json()
        return dict(Counter(r["class_id"] for r in data if r.get("class_id")))


async def get_classes_details(access_token: str) -> List[dict]:
    student_counts = await get_all_student_counts_by_class(access_token)

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/classes",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "id,code,active,capacity,level_id,levels!classes_level_id_fkey(code)"
            }
        )

        if res.status_code != 200:
            print(f"Erreur classes: {res.status_code}: {res.text}")
            return []

        classes = res.json()
        return [
            {
                "class_id": c["id"],
                "class_code": c["code"],
                "level_id": c["level_id"],
                "capacity": c["capacity"],
                "level_code": c.get("levels", {}).get("code"),
                "active": c["active"],
                "student_count": student_counts.get(c["id"], 0)
            }
            for c in classes
        ]


async def get_all_level_codes(access_token: str) -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/levels",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "code"
            }
        )

        if response.status_code != 200:
            print(f"Erreur {response.status_code}: {response.text}")
            return []

        data = response.json()
        return [item["code"] for item in data if "code" in item]


async def get_total_enrolled_students(access_token: str) -> int:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return 0

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/registrations",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json",
                "Prefer": "count=exact"
            },
            params={
                "select": "id",
                "year_id": f"eq.{year_id}"
            }
        )

        if response.status_code != 200:
            print(f"Erreur Supabase: {response.status_code} - {response.text}")
            return 0

        return len(response.json())


async def count_classes_by_section(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "id,level_id,levels!classes_level_id_fkey(section)"
            }
        )

        if response.status_code != 200:
            print(f"Erreur Supabase: {response.status_code} - {response.text}")
            return {"anglophone": 0, "francophone": 0}

        classes = response.json()

        # Compter les sections
        counter = Counter()
        for cls in classes:
            section = cls.get("levels", {}).get("section", "").strip().lower()
            if section in ["anglophone", "francophone"]:
                counter[section] += 1

        return {
            "anglophone": counter.get("anglophone", 0),
            "francophone": counter.get("francophone", 0)
        }


async def count_exam_classes(access_token: str) -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "id,level_id,levels!classes_level_id_fkey(examination)"
            }
        )

        if response.status_code != 200:
            print(f"Erreur Supabase: {response.status_code} - {response.text}")
            return 0

        classes = response.json()

        # Compter les classes dont le niveau est un niveau d'examen
        count = sum(1 for cls in classes if cls.get("levels", {}).get("examination") is True)

        return count


async def get_students_by_class_id(class_id: str, access_token: str) -> List[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    async with httpx.AsyncClient() as client:
        # Étape 1 : Récupérer l'année scolaire active
        year_resp = await client.get(
            f"{url}/rest/v1/years?select=id&active=eq.true",
            headers=headers
        )
        year_resp.raise_for_status()
        years = year_resp.json()
        if not years:
            return []

        active_year_id = years[0]["id"]

        # Étape 2 : Récupérer les élèves inscrits pour cette classe et cette année
        query_url = (
            f"{url}/rest/v1/registrations"
            f"?select=student_id,students(id,name,surname,gender)"
            f"&class_id=eq.{class_id}"
            f"&year_id=eq.{active_year_id}"
        )
        response = await client.get(query_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extraire les données des étudiants
        return [
            {
                "id": row["students"]["id"],
                "name": row["students"]["name"],
                "surname": row["students"]["surname"],
                "gender": row["students"]["gender"]
            }
            for row in data if row.get("students")
        ]


async def get_class_schedule(class_id: str, access_token: str) -> List[dict]:
    async with httpx.AsyncClient() as client:
        active_year_id = await get_active_year_id(access_token)
        print(active_year_id)
        # Étape 2 : récupérer les affectations pour cette classe et cette année
        affectation_url = (
            f"{url}/rest/v1/affectations"
            f"?select=id,day,slot,teacher_id,teachers(name,surname),"
            f"subject_id,subjects(short_name)"
            f"&class_id=eq.{class_id}&year_id=eq.{active_year_id}"
        )

        response = await client.get(
            affectation_url,
            headers={"Authorization": f"Bearer {access_token}", "apikey": key}
        )
        response.raise_for_status()
        rows = response.json()

        # Traitement pour valeurs nulles
        result = []
        for row in rows:
            teacher = row.get("teachers")
            subject = row.get("subjects")
            result.append({
                "id": row.get("id"),
                "day": row.get("day"),
                "slot": row.get("slot"),
                "teacher_id": row.get("teacher_id") or "",
                "teacher_name": f"{teacher.get('name', '')} {teacher.get('surname', '')}" if teacher else "",
                "subject_id": row.get("subject_id") or "",
                "short_name": subject.get("short_name", "") if subject else "",
            })

        return result


async def get_head_teacher_name(access_token: str, class_id: str, year_id: str) -> Optional[Dict[str, str]]:
    """
    Récupère le head‑teacher d'une classe donnée (classe + année) avec son nom.

    Returns
    -------
    dict  -> { "teacher_id": "...", "name": "...", "surname": "..." }
    None  -> si aucun head‑teacher n’est trouvé.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{url}/rest/v1/head_teachers",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                # jointure vers la vue secure_teachers
                "select": "teacher_id,secure_teachers(name,surname)",
                "class_id": f"eq.{class_id}",
                "year_id": f"eq.{year_id}",
                "limit": 1               # on ne veut qu’un seul résultat
            }
        )
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return ''

        item = data[0]
        return {
            "teacher_id": item["teacher_id"],
            "name": item["secure_teachers"]["name"],
            "surname": item["secure_teachers"]["surname"]
        }





















