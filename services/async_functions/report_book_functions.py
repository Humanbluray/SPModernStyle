from oauthlib.uri_validate import query
from postgrest import AsyncPostgrestClient
from services.supabase_client import *
import asyncio
import httpx
from urllib.parse import quote
from typing import List, Dict, Optional, Any


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


async def get_sequence_averages_with_details(access_token: str, year_id: str,) -> List[Dict]:
    """
    Récupère les lignes de sequence_averages pour une année et une séquence données,
    avec nom de l'élève, code de la classe et level_id.
    """

    # 🔹 Requête REST avec jointures
    request_url = (
        f"{url}/rest/v1/sequence_averages"
        "?select=*,"
        "students!inner(id,name,surname,image_url),"
        "classes!inner(id,code,level_id)"
        f"&year_id=eq.{year_id}"
        f"&order=class_id.asc"
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
        data = response.json()

    # 🔹 Reformater les données
    result = []
    for row in data:
        student = row.get("students", {})
        classe = row.get("classes", {})

        result.append({
            **row,  # tous les champs de sequence_averages
            "student_id": student.get("id"),
            "student_name": student.get("name"),
            "student_surname": student.get("surname"),
            "student_image": student.get("image_url"),
            "class_code": classe.get("code"),
            "level_id": classe.get("level_id"),
            "class_id": classe.get("id"),
        })

    return result


async def student_monthly_averages(access_token: str, year_id: str, sequence: str, page_number: int):
    """

    :param access_token:
    :param year_id:
    :param sequence:
    :param page_number:
    :return:
    """
    decalage = page_number * 100
    query_url = f"{url}/rest/v1/student_sequence_report_with_rank"
    params = {
        "select": "*",
        "limit": 100,
        "offset": decalage,
        "year_id": f"eq.{year_id}",
        "sequence": f"eq.{sequence}"
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


async def get_notes_by_student_sequence_year(access_token: str, student_id: str, sequence_id: str, year_id: str, ):
    """

    :param access_token:
    :param student_id:
    :param sequence_id:
    :param year_id:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/notes?select=id,"
        f"student_id,subject_id,sequence,year_id,value,coefficient," 
        f"subjects(id,name,short_name,group)"
        f"&student_id=eq.{student_id}"
        f"&sequence=eq.{sequence_id}"
        f"&year_id=eq.{year_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        notes = response.json()

    # Formatage des données pour ne garder que les paires clé-valeur avec le subject_short_name à plat
    formatted_notes = [
        {
            "id": n["id"],
            "student_id": n["student_id"],
            "subject_id": n["subject_id"],
            "sequence": n["sequence"],
            "year_id": n["year_id"],
            "value": n["value"],
            "coefficient": n["coefficient"],
            "subject_name": n["subjects"]["name"] if n.get("subjects") else None,
            "subject_short_name": n["subjects"]["short_name"] if n.get("subjects") else None,
            "subject_group": n["subjects"]["group"] if n.get("subjects") else None
        }
        for n in notes
    ]

    return formatted_notes


async def get_class_statistics_sequence(access_token: str, year_id: str, class_id: str, sequence: str) -> Dict:
    """
    :param access_token:
    :param class_id:
    :param year_id:
    :param sequence:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/classes_statistics?select=*"
        f"&class_id=eq.{class_id}&"
        f"&sequence=eq.{sequence}&"
        f"&year_id=eq.{year_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    # On force un seul résultat (si plusieurs, on prend le premier)
    return data[0] if data else None


async def get_student_basic_infos(access_token: str, student_id: str) -> Dict:
    """
    :param: access_token:
    :param : student_id:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/students?select=*"
        f"&id=eq.{student_id}"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    # On force un seul résultat (si plusieurs, on prend le premier)
    return data[0] if data else None


async def get_student_discipline_by_sequence(access_token: str, year_id: str, student_id: str, sequence: str)-> List[Dict]:
    """

    :param access_token:
    :param year_id:
    :param student_id:
    :param sequence:
    :return:
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }
    request_url = (
        f"{url}/rest/v1/discipline?select=*"
        f"&year_id=eq.{year_id}&"
        f"&student_id=eq.{student_id}&"
        f"&sequence=eq.{sequence}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)

    response.raise_for_status()
    return response.json()


async def get_student_registration_details(access_token: str, year_id: str, student_id: str) -> List[Dict]:
    """
    Récupère les détails d'inscription d'un étudiant en incluant les informations
    sur l'étudiant, la classe et le professeur principal pour une année donnée.

    Args:
        access_token (str): Le jeton d'accès de l'utilisateur.
        year_id (str): L'ID de l'année scolaire.
        student_id (str): L'ID de l'étudiant.

    Returns:
        List[Dict]: Une liste de dictionnaires contenant les détails ou une liste vide si non trouvé.
    """

    # La requête de jointure est définie ici
    # La syntaxe de Supabase/PostgREST utilise le point-virgule pour lier les tables
    select_query = (
        "*, "  # Sélectionne toutes les colonnes de la table 'registrations'
        "students(*), "  # Sélectionne toutes les colonnes de la table 'students' liée
        "classes:class_id(code, count:registrations(count)), "  # Sélectionne le code de la classe et son effectif
        "head_teachers:class_id(teachers(name, surname))"  # Sélectionne le nom du professeur principal
    )

    request_url = (
        f"{URL}/rest/v1/registrations?select={select_query}"
        f"&student_id=eq.{student_id}"
        f"&year_id=eq.{year_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur 4xx/5xx

    return response.json()


async def get_student_sequence_detail(access_token: str, student_id: str, sequence: str, year_id: str):
    """

    :param access_token:
    :param student_id:
    :param sequence:
    :param year_id:
    :return:
    """
    query_url = f"{url}/rest/v1/student_sequence_report_with_rank"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=query_url,
            headers=headers,
            params={
                "student_id": f"eq.{student_id}",
                "sequence": f"eq.{sequence}",
                "year_id": f"eq.{year_id}",
                "limit": 1  # force un seul résultat
            },
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None


async def get_student_subject_stats(access_token: str, student_id: str, sequence: str, year_id: str):
    """
    Récupère toutes les notes et statistiques d'un élève pour chaque matière
    sur une séquence donnée et une année scolaire.

    :param access_token: jeton RLS pour Supabase
    :param student_id: ID de l'élève
    :param year_id: ID de l'année scolaire
    :param sequence: nom de la séquence
    :return: liste de dictionnaires JSON, une ligne par matière
    """
    query_url = f"{url}/rest/v1/vw_student_subject_stats"
    params = {
        "student_id": f"eq.{student_id}",
        "year_id": f"eq.{year_id}",
        "sequence": f"eq.{sequence}",
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


async def get_all_students_id_by_class(access_token: str, class_id: str, year_id: str) -> List[Dict]:
    """
    retourne la liste des ids de tous les élèves
    :param access_token:
    :param class_id:
    :param year_id:
    :return:
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    query_url = (
        f"{url}/rest/v1/registrations"
    )
    params = {
        "select": "student_id",
        "class_id": f"eq.{class_id}",
        "year_id": f"eq.{year_id}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(query_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

    return data


