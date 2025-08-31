from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client, app_url
import asyncio
import httpx
from typing import List, Dict, Optional, Any
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


async def current_year_data(access_token) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/years?active=eq.true&select=*",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
        )
        data = response.json()
        return data[0] if data else None


async def get_all_sequences(access_token: str) -> List[Dict]:
    """
    Récupère tous les enregistrements de la table 'sequences'.
    Retourne une liste de dictionnaires avec tous les champs.
    """
    request_url = f"{url}/rest/v1/sequences?select=*&order=name.asc"

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


async def get_all_years(access_token: str) -> List[Dict]:
    """
    Récupère tous les enregistrements de la table 'sequences'.
    Retourne une liste de dictionnaires avec tous les champs.
    """
    request_url = f"{url}/rest/v1/years?select=*&order=name.asc"

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


async def get_all_quarters(access_token: str) -> List[Dict]:
    """
    Récupère tous les enregistrements de la table 'sequences'.
    Retourne une liste de dictionnaires avec tous les champs.
    """
    request_url = f"{url}/rest/v1/quarters?select=*&order=name.asc"

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


async def update_sequence_active_status(access_token: str, sequence_name: str, active: bool) -> dict:
    """
    Met à jour le champ 'active' d'une séquence donnée.

    Parameters
    ----------
    sequence_name : str   -> le nom de la séquence (clé primaire)
    active : bool         -> True ou False
    """
    request_url = f"{url}/rest/v1/sequences?name=eq.{sequence_name}"

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={"active": active}
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}


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


async def update_quarter_active_status(access_token: str, quarter_name: str, active: bool) -> dict:
    """
    Met à jour le champ 'active' d'une séquence donnée.

    Parameters
    ----------
    quarter_name : str   -> le nom de la séquence (clé primaire)
    active : bool         -> True ou False
    """
    request_url = f"{url}/rest/v1/quarters?name=eq.{quarter_name}"

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={"active": active}
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}


async def get_classes_with_student_count(access_token: str, year_id: str) -> List[Dict]:
    """
    Retourne la liste des classes (class_id, class_name, level_id, effectif)
    ayant au moins un élève inscrit pour une année donnée.
    """
    # ✅ Astuce : on utilise la jointure registrations->classes pour tout récupérer
    request_url = (
        f"{url}/rest/v1/registrations"
        f"?select=class_id,classes(id,code,level_id)"
        f"&year_id=eq.{year_id}"
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

    # 🔹 Calcul de l'effectif par classe
    classes_dict = {}
    for row in data:
        cls = row["classes"]
        if not cls:  # sécurité si class_id NULL
            continue

        class_id = cls["id"]
        if class_id not in classes_dict:
            classes_dict[class_id] = {
                "class_id": class_id,
                "class_name": cls["code"],
                "level_id": cls["level_id"],
                "effectif": 0
            }
        classes_dict[class_id]["effectif"] += 1

    # Convertir en liste
    return list(classes_dict.values())


async def get_subjects_by_level(access_token: str, level_id: str) -> List[Dict]:
    """
    Retourne la liste des matières (id, name, short_name)
    pour un level_id donné, triée par name.
    """
    request_url = (
        f"{url}/rest/v1/subjects"
        f"?select=id,name,short_name&level_id=eq.{level_id}&order=name.asc"
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


async def get_all_registered_students_by_year(access_token: str, year_id: str) -> List[Dict]:
    """
    Retourne la liste des élèves inscrits pour une année donnée
    (student_id, student_name, student_surname, class_id, class_code)
    """

    # ✅ Jointure registrations -> students + classes
    request_url = (
        f"{url}/rest/v1/registrations"
        f"?select=student_id,students(name,surname),class_id,classes(code)"
        f"&year_id=eq.{year_id}"
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

    # 🔹 Construire le résultat
    result = [
        {
            "student_id": row["student_id"],
            "student_name": row["students"]["name"],
            "student_surname": row["students"]["surname"],
            "class_id": row["class_id"],
            "class_code": row["classes"]["code"]
        }
        for row in data
        if row.get("students") and row.get("classes")  # sécurité
    ]

    return result


async def get_notes_for_student_sequence(access_token: str, student_id: str, year_id: str, sequence: str) -> List[Dict]:
    """
    Retourne toutes les notes d'un élève pour une année et une séquence donnée
    avec les infos sur la matière.
    """

    # ✅ On sélectionne notes + subjects + students
    request_url = (
        f"{url}/rest/v1/notes"
        "?select=id,value,coefficient,"
        "subjects!inner(id,name,short_name),"
        "students!inner(id,name,surname)"
        f"&student_id=eq.{student_id}"
        f"&year_id=eq.{year_id}"
        f"&sequence=eq.{sequence}"
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

    # 🔹 Construire le résultat sans KeyError
    result = []
    for row in data:
        subject = row.get("subjects")
        student = row.get("students")

        # On ne prend que si la jointure a bien fonctionné
        if subject and student:
            result.append({
                "note_id": row["id"],
                "value": row.get("value"),
                "coefficient": row.get("coefficient"),
                "subject_id": subject.get("id"),
                "subject_name": subject.get("name"),
                "subject_short_name": subject.get("short_name"),
                "student_id": student.get("id"),
                "student_name": student.get("name"),
                "student_surname": student.get("surname"),
            })

    return result


async def insert_sequence_average(access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insère une nouvelle ligne dans la table sequence_averages
    :param access_token: Token JWT de l'utilisateur
    :param urL: URL de ton projet Supabase
    :param key: Clé API Supabase
    :param data: Dictionnaire avec les colonnes à insérer, ex:
                 {
                    "student_id": "...",
                    "year_id": "...",
                    "class_id": "...",
                    "value": 14.5,
                    "sequence": "sequence 1",
                    "quarter": "trimestre 1",
                    "points": 29.0,
                    "total_coefficient": 2
                 }
    :return: La ligne insérée
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{url}/rest/v1/sequence_averages",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Pour renvoyer la ligne insérée
            },
            json=data
        )

        # Vérifie et renvoie le JSON
        response.raise_for_status()
        return response.json()[0] if response.json() else {}


async def get_affectations_by_year_simple(
        access_token: str,
        year_id: str
) -> List[Dict]:
    """
    Récupère toutes les affectations pour une année donnée
    sans jointures.
    """

    request_url = (
        f"{url}/rest/v1/affectations"
        f"?year_id=eq.{year_id}"
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


import httpx
from typing import Dict


async def insert_year(
        access_token: str,
        year_data: Dict
) -> Dict:
    """
    Insère une nouvelle année scolaire dans la table 'years'.

    :param access_token: Jeton d'accès (Bearer)
    :param urL: URL de base du projet Supabase
    :param key: API key
    :param year_data: Dictionnaire contenant les champs à insérer, ex :
        {
            "name": "2025-2026",
            "active": True,
            "short": 2025,
            "start": "2025-09-01",
            "end": "2026-06-30"
        }
    :return: La ligne insérée sous forme de dictionnaire
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{url}/rest/v1/years",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Pour renvoyer la ligne insérée
            },
            json=year_data
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else {}


async def update_year_by_id(
        access_token: str,
        year_id: str,
        update_data: Dict
) -> Dict:
    """
    Met à jour une année scolaire dans la table 'years' en fonction de son ID.

    :param access_token: Jeton d'accès (Bearer)
    :param urL: URL de base du projet Supabase
    :param key: API key
    :param year_id: ID de l'année à mettre à jour
    :param update_data: Dictionnaire des champs à mettre à jour, ex :
        {
            "active": False,
            "end": "2026-07-01"
        }
    :return: La ligne mise à jour sous forme de dictionnaire
    """

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{url}/rest/v1/years?id=eq.{year_id}",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Pour renvoyer la ligne modifiée
            },
            json=update_data
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else {}


import httpx
from typing import Dict


async def insert_affectation(
        access_token: str,
        affectation_data: Dict
) -> Dict:
    """
    Insère une nouvelle ligne dans la table 'affectations'.

    :param access_token: Jeton d'accès (Bearer)
    :param urL: URL de base Supabase
    :param key: API Key
    :param affectation_data: Dictionnaire contenant les champs à insérer, ex :
        {
            "year_id": "uuid",
            "teacher_id": "uuid",
            "class_id": "uuid",
            "subject_id": "uuid",
            "nb_hour": 4,
            "day": "Monday",
            "slot": "08:00-10:00",
            "busy": False
        }
    :return: La ligne insérée sous forme de dictionnaire
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{url}/rest/v1/affectations",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Pour renvoyer la ligne insérée
            },
            json=affectation_data
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else {}


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


async def get_sequence_averages_by_year_and_sequence(
    access_token: str,
    year_id: str,
    sequence: str
):
    """
    Récupère toutes les données de la table sequence_averages
    pour un year_id et une sequence donnés.

    :param access_token: Jeton d'accès utilisateur (Bearer token)
    :param url: URL de base Supabase
    :param key: Clé API publique Supabase
    :param year_id: ID de l'année scolaire
    :param sequence: Nom ou identifiant de la séquence
    :return: Liste de dictionnaires contenant les enregistrements
    """
    request_url = (
        f"{url}/rest/v1/sequence_averages"
        f"?select=*"
        f"&year_id=eq.{year_id}"
        f"&sequence=eq.{sequence}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()  # Lève une exception si HTTP != 2xx
        return response.json()


async def insert_class_average(
    access_token: str,
    data: dict
):
    """
    Insère une nouvelle ligne dans la table classes_averages.

    :param access_token: Jeton d'accès utilisateur (Bearer token)
    :param url: URL de base Supabase
    :param key: Clé API publique Supabase
    :param data: Dictionnaire avec les colonnes et valeurs à insérer
    :return: Ligne insérée
    """
    request_url = f"{url}/rest/v1/classes_statistics"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Content-Type": "application/json",
        "Prefer": "return=representation"  # pour retourner la ligne insérée
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(request_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()







