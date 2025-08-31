from services.supabase_client import url, key, supabase_client
import asyncio
import httpx
from typing import List, Dict


async def get_all_classes_basic_info(access_token: str) -> List[Dict]:
    """
    retourne l'id et le code des classes
    :param access_token:
    :return:
    """
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


async def get_active_year_id(access_token) -> str:
    """
    donne l'uid de l'année scolaire active
    :param access_token:
    :return:
    """
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


async def get_all_notes_with_details(
    access_token: str, year_id: str, subject_id: str, class_id: str, sequence: str
) -> list[dict]:
    """

    :param access_token:
    :param year_id:
    :param subject_id:
    :param class_id:
    :param sequence:
    :return:
    """
    query_url = f"{url}/rest/v1/notes_view"
    params = {
        "select": "*",
        "year_id": f"eq.{year_id}",
        "subject_id": f"eq.{subject_id}",
        "class_id": f"eq.{class_id}",
        "sequence": f"eq.{sequence}",
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


async def get_all_notes(
    page_number: int, access_token: str, year_id: str,
) -> list[dict]:
    """"""
    decalage = page_number * 100
    query_url = f"{url}/rest/v1/notes_view"
    params = {
        "select": "*",
        "limit": 100,
        "offset": decalage,
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


async def get_students_without_note_for_subject(
    access_token: str,
    class_id: str,
    sequence: str,
    subject_id: str,
    year_id: str
) -> list[dict]:

    """
    Retourne la liste des élèves sans note pour une matière donnée,
    une classe et une séquence, avec détails classe et matière.
    Optimisé avec jointures PostgREST.
    """

    async with httpx.AsyncClient() as client:
        # 2️⃣ Requête pour récupérer les élèves inscrits à cette classe/année
        #    + infos classe
        reg_url = (
            f"{url}/rest/v1/registrations"
            f"?select=student_id,students(name,surname),class_id,classes(code),year_id"
            f"&class_id=eq.{class_id}&year_id=eq.{year_id}"
        )
        reg_resp = await client.get(
            reg_url,
            headers={"apikey": key, "Authorization": f"Bearer {access_token}"}
        )
        reg_resp.raise_for_status()
        registrations = reg_resp.json()

        if not registrations:
            return []

        # 3️⃣ Requête pour récupérer uniquement les student_id qui ont déjà une note
        notes_url = (
            f"{url}/rest/v1/notes"
            f"?select=student_id"
            f"&year_id=eq.{year_id}&class_id=eq.{class_id}"
            f"&sequence=eq.{sequence}&subject_id=eq.{subject_id}"
        )
        notes_resp = await client.get(
            notes_url,
            headers={"apikey": key, "Authorization": f"Bearer {access_token}"}
        )
        notes_resp.raise_for_status()
        noted_student_ids = {n["student_id"] for n in notes_resp.json()}

        # 4️⃣ Requête pour récupérer la matière une seule fois
        subject_url = (
            f"{url}/rest/v1/subjects"
            f"?select=id,name,short_name&id=eq.{subject_id}"
        )
        subject_resp = await client.get(
            subject_url,
            headers={"apikey": key, "Authorization": f"Bearer {access_token}"}
        )
        subject_resp.raise_for_status()
        subject_info = subject_resp.json()[0] if subject_resp.json() else {}

    # 5️⃣ Filtrer les élèves sans note et construire le résultat
    result = []
    for reg in registrations:
        sid = reg["student_id"]
        if sid not in noted_student_ids:
            result.append({
                "student_id": sid,
                "name": reg["students"]["name"],
                "surname": reg["students"]["surname"],
                "class_id": reg["class_id"],
                "class_name": reg["classes"]["code"],
                "subject_id": subject_info.get("id"),
                "subject_name": subject_info.get("name"),
                "subject_short_name": subject_info.get("short_name")
            })

    return result


async def get_teacher_classes(access_token: str, teacher_id: str,) -> list[dict]:
    """
    donne les classes dans lesquelles un seignant est affecté pour l'année scoalire en cours
    :param access_token:
    :param teacher_id:
    :return:
    """
    active_year_id = await get_active_year_id(access_token)

    # 2. Récupérer les classes distinctes du prof pour l'année active
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/affectations",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Prefer": "params=distinct"
            },
            params={
                "select": "class_id,classes(code)",
                "teacher_id": f"eq.{teacher_id}",
                "year_id": f"eq.{active_year_id}"
            }
        )
        response.raise_for_status()
        affectations = response.json()

        # On transforme le résultat en liste de dicts {class_id, class_code}
        unique_classes = []
        seen = set()

        for item in affectations:
            class_id = item["class_id"]
            class_code = item["classes"]["code"] if item.get("classes") else None

            if class_id not in seen:
                seen.add(class_id)
                unique_classes.append({
                    "class_id": class_id,
                    "class_code": class_code
                })

        return unique_classes


async def get_teacher_subjects_for_class(access_token: str, teacher_id: str, class_id: str) -> list[dict]:
    """
    Donne les matières enseignées par un professeur dans une classe donnée
    :param access_token:
    :param teacher_id:
    :param class_id:
    :return:
    """
    active_year_id = await get_active_year_id(access_token)

    # 2. Récupération des matières (subjects) enseignées
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/affectations",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Prefer": "params=distinct"
            },
            params={
                "select": "subject_id,subjects(name)",
                "teacher_id": f"eq.{teacher_id}",
                "class_id": f"eq.{class_id}",
                "year_id": f"eq.{active_year_id}"
            }
        )
        response.raise_for_status()
        affectations = response.json()

        # Transformation du résultat en liste de dictionnaires uniques
        unique_subjects = []
        seen = set()

        for item in affectations:
            subject_id = item["subject_id"]
            subject_name = item["subjects"]["name"] if item.get("subjects") else None

            if subject_id not in seen:
                seen.add(subject_id)
                unique_subjects.append({
                    "subject_id": subject_id,
                    "subject_name": subject_name
                })

        return unique_subjects


async def get_subject_coefficient(access_token: str, subject_id: str) -> int | None:
    """
    donne le coefficient d'une matière à partir de son id
    :param access_token:
    :param subject_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/subjects",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "id": f"eq.{subject_id}",
                "select": "coefficient",
                "limit": 1
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0].get("coefficient")
        return None


async def get_subjects_by_class_id(access_token: str, class_id: str) -> list[dict]:
    """
    à partir de l'id d'une classe on retrouve les matières
    :param access_token:
    :param class_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        # 1. Récupérer le level_id de la classe
        class_resp = await client.get(
            f"{url}/rest/v1/classes",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "id": f"eq.{class_id}",
                "select": "level_id",
                "limit": 1
            }
        )
        class_resp.raise_for_status()
        class_data = class_resp.json()

        if not class_data:
            return []

        level_id = class_data[0]["level_id"]

        # 2. Récupérer les matières liées à ce niveau
        subjects_resp = await client.get(
            f"{url}/rest/v1/subjects",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "level_id": f"eq.{level_id}",
                "select": "id,name",
                "order": "name.asc"
            }
        )
        subjects_resp.raise_for_status()
        subjects = subjects_resp.json()

        return [
            {"subject_id": s["id"], "subject_name": s["name"]}
            for s in subjects
        ]


async def get_subject_details(access_token: str, subject_id: str) -> dict | None:
    """
    toutes les infos à partir de l'id d'une matière
    :param access_token:
    :param subject_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/subjects",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "id": f"eq.{subject_id}",
                "select": "*",
                "limit": 1
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]  # retourne toutes les infos du sujet
        return None


async def get_class_details(access_token: str, class_id: str) -> dict | None:
    """
    tous les détails d'une classe à partir de son id
    :param access_token:
    :param class_id:
    :return:
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "id": f"eq.{class_id}",
                "select": "*",  # sélection de tous les champs
                "limit": 1
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]  # retourne tous les détails de la classe
        return None


async def note_exists(access_token: str, student_id: str, year_id: str, sequence: str, subject_id: str) -> bool:
    """
    vérifie si une note existe ou pas
    :param access_token:
    :param student_id:
    :param year_id:
    :param sequence:
    :param subject_id:
    :return: True si elle existe et False dans le cas contraire
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/notes",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
            params={
                "student_id": f"eq.{student_id}",
                "year_id": f"eq.{year_id}",
                "sequence": f"eq.{sequence}",
                "subject_id": f"eq.{subject_id}",
                "select": "id",
                "limit": 1
            }
        )
        response.raise_for_status()
        data = response.json()
        return len(data) > 0


async def insert_note(access_token: str, note_data: dict) -> bool:
    """
    Insère une nouvelle note dans la table 'notes'.

    Params:
        access_token (str): jeton d'accès.
        note_data (dict): dictionnaire avec les champs de la note à insérer.
    Returns:
        bool: True si l'insertion a réussi, False sinon.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{url}/rest/v1/notes",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"  # on ne veut pas le résultat en retour
            },
            json=note_data
        )
        if response.status_code in [200, 201, 204]:
            return True
        else:
            print("Erreur insertion:", response.text)
            return False


async def get_statistics_by_class_subject(
    access_token: str, year_id: str, class_id: str, subject_id: str, sequence: str
):
    """

    :param access_token:
    :param year_id:
    :param class_id:
    :param subject_id:
    :param sequence:
    :return:
    """
    query_url = f"{url}/rest/v1/vw_subject_class_sequence_stats"
    params = {
        "year_id": f"eq.{year_id}",
        "class_id": f"eq.{class_id}",
        "subject_id": f"eq.{subject_id}",
        "sequence": f"eq.{sequence}",
        "select": "*",  # tous les champs
        "limit": 1
    }
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=query_url, params=params, headers=headers
        )

    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]  # retourne le premier et unique résultat
        else:
            raise Exception("Aucun résultat trouvé")
    else:
        raise Exception(f"Erreur {response.status_code}: {response.text}")














