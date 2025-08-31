from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client
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


async def get_all_teachers(access_token: str) -> List[dict]:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        # 1. Récupérer l’année active
        active_year_id = await get_active_year_id(access_token)

        # 2. Récupérer tous les professeurs
        teachers_response = await client.get(
            f"{url}/rest/v1/secure_teachers?select=id,name,surname,gender,contact,pay,subjects",
            headers=headers
        )
        teachers_response.raise_for_status()
        teachers = teachers_response.json()

        # 3. Récupérer les id des profs qui sont titulaires pour l’année active
        head_teachers_response = await client.get(
            f"{url}/rest/v1/head_teachers?select=teacher_id&year_id=eq.{active_year_id}",
            headers=headers
        )
        head_teachers_response.raise_for_status()
        head_teachers_data = head_teachers_response.json()
        head_teacher_ids = {row["teacher_id"] for row in head_teachers_data if row["teacher_id"]}

        # 4. Ajouter la clé is_head_teacher à chaque prof
        for teacher in teachers:
            teacher["is_head_teacher"] = teacher["id"] in head_teacher_ids

        return teachers


async def get_all_distinct_subject_short_names(access_token: str) -> List[str]:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/subjects?select=short_name",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        # On extrait les short_names non nuls et on supprime les doublons
        seen = set()
        distinct_short_names = []
        for row in data:
            name = row.get("short_name")
            if name and name not in seen:
                seen.add(name)
                distinct_short_names.append(name)

        return distinct_short_names


async def get_teacher_affectations(teacher_id: str, access_token: str) -> List[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key  # supprime si inutile
    }

    year_id = await get_active_year_id(access_token)

    my_url = (
        f"{url}/rest/v1/affectations"
        "?select=id,year_id,teacher_id,subject_id,class_id,day,slot,nb_hour,"
        "subjects(name,short_name),classes(code),secure_teachers(id)"  # jointure vers vue
        f"&teacher_id=eq.{teacher_id}&year_id=eq.{year_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(my_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    results = []

    for row in data:
        results.append({
            "id": row.get("id"),
            "year_id": row.get("year_id"),
            "teacher_id": row.get("teacher_id"),
            "subject_id": row.get("subject_id"),
            "class_id": row.get("class_id"),
            "day": row.get("day"),
            "slot": row.get("slot"),
            "nb_hour": row.get("nb_hour"),
            "subject_name": row.get("subjects", {}).get("name", ""),
            "subject_short_name": row.get("subjects", {}).get("short_name", ""),
            "class_code": row.get("classes", {}).get("code", "")
        })

    return results


async def get_all_affectations_details(access_token: str) -> List[dict]:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    # Utilisation de la vue secure_teachers
    my_url = (
        f"{url}/rest/v1/affectations"
        "?select=id,day,slot,nb_hour,busy,teacher_id,subject_id,class_id,"
        "secure_teachers!affectations_teacher_id_fkey(name,surname),"
        "subjects(name,short_name),"
        "classes(code)"
        f"&year_id=eq.{year_id}"
        f"&order=slot.asc"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(my_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    results = []
    for row in data:
        teacher = row.get("secure_teachers")
        subject = row.get("subjects")

        teacher_id = row.get("teacher_id")
        subject_id = row.get("subject_id")

        results.append({
            "id": row.get("id"),
            "day": row.get("day"),
            "slot": row.get("slot"),
            "nb_hour": row.get("nb_hour"),
            "busy": row.get("busy", False),
            "teacher_id": teacher_id,
            "subject_id": subject_id,
            "class_id": row.get("class_id"),
            "teacher_name": f"{teacher.get('name', '') if teacher else None}",
            "teacher_surname": f"{teacher.get('surname', '') if teacher else None}",
            "subject_name": subject.get("name", "") if subject else None,
            "subject_short_name": subject.get("short_name", "") if subject else None,
            "class_code": row.get("classes", {}).get("code", ""),
            "status": bool(teacher_id and subject_id)
        })

    return results


async def is_teacher_busy(teacher_id: str, day: str, slot: str, access_token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    year_id = await get_active_year_id(access_token)

    url_query = (
        f"{url}/rest/v1/affectations"
        "?select=id,day,slot,class_id,subject_id,teacher_id,"
        "secure_teachers(name,surname),"
        "subjects(name,short_name),"
        "classes(code)"
        f"&teacher_id=eq.{teacher_id}&day=eq.{day}&slot=eq.{slot}&year_id=eq.{year_id}&limit=1"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_query, headers=headers)
        response.raise_for_status()
        data = response.json()

    if data:
        row = data[0]
        return {
            "id": row.get("id"),
            "day": row.get("day"),
            "slot": row.get("slot"),
            "teacher_id": row.get("teacher_id"),
            "teacher_name": f"{row.get('teachers', {}).get('surname', '')} {row.get('teachers', {}).get('name', '')}".strip(),
            "subject_id": row.get("subject_id"),
            "subject_name": row.get("subjects", {}).get("name", ""),
            "subject_short_name": row.get("subjects", {}).get("short_name", ""),
            "class_id": row.get("class_id"),
            "class_code": row.get("classes", {}).get("code", ""),
            "status": True
        }
    else:
        return {
            "id": None,
            "day": day,
            "slot": slot,
            "teacher_id": None,
            "teacher_name": None,
            "subject_id": None,
            "subject_name": None,
            "subject_short_name": None,
            "class_id": None,
            "class_code": None,
            "status": False
        }


async def get_teacher_affectations_details(teacher_id: str, access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key  # supprime si inutile
    }

    year_id = await get_active_year_id(access_token)

    url_query = (
        f"{url}/rest/v1/affectations"
        "?select=id,day,slot,year_id,class_id,subject_id,teacher_id,"
        "secure_teachers!affectations_teacher_id_fkey(name,surname),"
        "subjects(name,short_name),"
        "classes(code)"
        f"&teacher_id=eq.{teacher_id}&year_id=eq.{year_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_query, headers=headers)
        response.raise_for_status()
        data = response.json()

    results = []
    for row in data:
        teacher = row.get("teachers") or {}
        subject = row.get("subjects") or {}
        class_ = row.get("classes") or {}

        results.append({
            "id": row.get("id"),
            "year_id": row.get("year_id"),
            "day": row.get("day"),
            "slot": row.get("slot"),
            "teacher_id": row.get("teacher_id"),
            "teacher_name": f"{teacher.get('name', '')}",
            "subject_id": row.get("subject_id"),
            "subject_name": subject.get("name", ""),
            "subject_short_name": subject.get("short_name", ""),

            "class_id": row.get("class_id"),
            "class_code": class_.get("code", ""),
            "status": True
        })

    return results


async def get_subjects_by_level_id(level_id: str, access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key  # remplace par ta vraie clé si nécessaire
    }

    url_request = (
        f"{url}/rest/v1/subjects"
        f"?select=id,short_name,name"
        f"&level_id=eq.{level_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_request, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data


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


async def get_level_by_class_id(classe_id: str, access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    url_request = (
        f"{url}/rest/v1/classes"
        f"?select=level_id"
        f"&id=eq.{classe_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_request, headers=headers)
        response.raise_for_status()
        data = response.json()

    # On retourne le premier résultat s'il existe
    return data[0] if data else None


async def is_class_slot_occupied(
    class_id: str,
    day: str,
    slot: str,
    access_token: str
) -> Dict[str, bool]:
    year_id  = await get_active_year_id(access_token)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    url_query = (
        f"{url}/rest/v1/affectations"
        f"?select=teacher_id,subject_id"
        f"&class_id=eq.{class_id}"
        f"&year_id=eq.{year_id}"
        f"&day=eq.{day}"
        f"&slot=eq.{slot}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_query, headers=headers)
        response.raise_for_status()
        data = response.json()

    if not data:
        return {"occupied": False}

    for record in data:
        if record.get("teacher_id") is not None or record.get("subject_id") is not None:
            return {"occupied": True}

    return {"occupied": False}


async def get_hourly_load_by_subject_id(subject_id: str, access_token: str) -> int:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    my_url = (
        f"{url}/rest/v1/subjects"
        f"?select=hourly_load"
        f"&id=eq.{subject_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(my_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    if data:
        return data[0].get("hourly_load", 0)
    else:
        return 0


async def count_affectations_by_subject_and_class(subject_id: str, class_id: str, access_token: str) -> int:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    # Obtenir l'année active
    year_id = await get_active_year_id(access_token)

    url_query = (
        f"{url}/rest/v1/affectations"
        f"?select=id"
        f"&subject_id=eq.{subject_id}"
        f"&class_id=eq.{class_id}"
        f"&year_id=eq.{year_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_query, headers=headers)
        response.raise_for_status()
        data = response.json()

    return len(data)


async def get_teacher_subjects_for_level(teacher_id: str, level_id: str, access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    # 1. Récupérer la liste des short_names depuis teachers.subjects
    async with httpx.AsyncClient() as client:
        teacher_res = await client.get(
            f"{url}/rest/v1/secure_teachers",
            headers=headers,
            params={
                "select": "subjects",
                "id": f"eq.{teacher_id}"
            }
        )
        teacher_res.raise_for_status()
        teacher_data = teacher_res.json()
        if not teacher_data or not teacher_data[0].get("subjects"):
            return []

        teacher_subjects = teacher_data[0]["subjects"]  # c'est une liste

    # 2. Récupérer les subjects correspondant au level_id et dont short_name est dans teacher_subjects
    async with httpx.AsyncClient() as client:
        subjects_res = await client.get(
            f"{url}/rest/v1/subjects",
            headers=headers,
            params={
                "select": "id,short_name",
                "level_id": f"eq.{level_id}"
            }
        )
        subjects_res.raise_for_status()
        subjects_data = subjects_res.json()

    # 3. Filtrer localement selon les short_name que le prof enseigne
    matching_subjects = [
        {"id": s["id"], "short_name": s["short_name"]}
        for s in subjects_data
        if s["short_name"] in teacher_subjects
    ]

    return matching_subjects


async def get_class_subjects_with_affectations(access_token: str, class_id: str) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # Étape 1 : Récupérer le level_id de la classe
        class_res = await client.get(
            f"{url}/rest/v1/classes",
            headers=headers,
            params={
                "select": "level_id",
                "id": f"eq.{class_id}"
            }
        )

        if class_res.status_code != 200 or not class_res.json():
            print("Erreur récupération classe:", class_res.text)
            return []

        level_id = class_res.json()[0]["level_id"]

        # Étape 2 : Récupérer les matières liées à ce niveau
        subjects_res = await client.get(
            f"{url}/rest/v1/subjects",
            headers=headers,
            params={
                "select": "id,name,short_name,hourly_load",
                "level_id": f"eq.{level_id}"
            }
        )

        if subjects_res.status_code != 200:
            print("Erreur récupération matières:", subjects_res.text)
            return []

        subjects = subjects_res.json()
        results = []

        # Étape 3 : Pour chaque matière, compter les affectations dans cette classe
        for subject in subjects:
            subject_id = subject["id"]

            affectations_res = await client.get(
                f"{url}/rest/v1/affectations",
                headers=headers,
                params={
                    "select": "id",
                    "class_id": f"eq.{class_id}",
                    "subject_id": f"eq.{subject_id}"
                }
            )

            if affectations_res.status_code != 200:
                print(f"Erreur affectations pour subject {subject_id}:", affectations_res.text)
                continue

            affectation_count = len(affectations_res.json())

            results.append({
                "subject_id": subject_id,
                "short_name": subject["short_name"],
                "name": subject["name"],
                "hourly load": subject["hourly_load"],
                "nombre_affectations": affectation_count
            })

        return results


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


async def get_head_class_code_by_teacher_id(access_token: str, teacher_id: str, year_id: str) -> str | None:
    """
    Récupère le code de la classe d'un head_teacher à partir de son teacher_id et de l'année.
    """
    async with httpx.AsyncClient() as client:
        url_request = (
            f"{url}/rest/v1/head_teachers"
            f"?select=classes(code)"
            f"&teacher_id=eq.{teacher_id}&year_id=eq.{year_id}"
        )

        response = await client.get(
            url_request,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

        if data and "classes" in data[0]:
            return data[0]["classes"]["code"]
        return None


async def get_non_head_teachers(access_token: str, year_id: str,) -> List[Dict[str, str]]:
    """
    Récupère la liste des professeurs qui ne sont pas head_teachers pour une année donnée.

    Returns:
    -------
    Une liste de dictionnaires : { "id": "...", "name": "...", "surname": "..." }
    """
    async with httpx.AsyncClient() as client:
        # Étape 1 : récupérer les IDs des head_teachers pour l'année
        head_teachers_url = (
            f"{url}/rest/v1/head_teachers"
            f"?select=teacher_id"
            f"&year_id=eq.{year_id}"
        )

        response = await client.get(
            head_teachers_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        head_teacher_ids = [item["teacher_id"] for item in response.json()]

        # Étape 2 : récupérer tous les teachers
        teachers_url = (
            f"{url}/rest/v1/teachers"
            f"?select=id,name,surname"
        )
        response = await client.get(
            teachers_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        all_teachers = response.json()

        # Étape 3 : filtrer localement ceux qui ne sont pas head_teachers
        non_head_teachers = [
            teacher for teacher in all_teachers if teacher["id"] not in head_teacher_ids
        ]

        return non_head_teachers


async def get_classes_without_head_teacher(access_token: str, year_id: str,) -> List[dict]:
    """
    Retourne les classes qui n'ont pas de head_teacher pour une année donnée.
    """
    async with httpx.AsyncClient() as client:
        # Étape 1 : récupérer les class_id dans head_teachers pour l'année
        head_teachers_url = (
            f"{url}/rest/v1/head_teachers"
            f"?select=class_id"
            f"&year_id=eq.{year_id}"
        )

        response = await client.get(
            head_teachers_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        assigned_class_ids = [item["class_id"] for item in response.json()]

        # Étape 2 : récupérer toutes les classes
        classes_url = f"{url}/rest/v1/classes?select=id,code"
        response = await client.get(
            classes_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        all_classes = response.json()

        # Étape 3 : filtrer les classes sans head_teacher
        unassigned_classes = [
            classe for classe in all_classes if classe["id"] not in assigned_class_ids
        ]

        return unassigned_classes



async def get_class_subjects_hours(access_token: str, class_id: str, year_id: str):
    """

    :param access_token:
    :param class_id:
    :param year_id:
    :return:
    """
    query_url = f"{url}/rest/v1/class_subjects_hours"
    params = {
        "class_id": f"eq.{class_id}",
        "year_id": f"eq.{year_id}",
        "select": "*"
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url=query_url, params=params, headers=headers)
        response.raise_for_status()  # lève une erreur si status != 200
        return response.json()  # renvoie toutes les lignes correspondant aux filtres







