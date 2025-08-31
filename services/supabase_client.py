import os, pandas, openpyxl
from dotenv import load_dotenv
from pandas.io.common import file_path_to_url
from supabase import create_client

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
app_url = os.getenv('APP_URL')

school_name_fr = os.getenv('SCHOOL_NAME_FR')
school_name_en = os.getenv('SCHOOL_NAME_EN')
school_code = os.getenv('SCHOOL_CODE')
school_delegation_fr = os.getenv('SCHOOL_DELEGATION_FR')
school_delegation_en = os.getenv('SCHOOL_DELEGATION_EN')
national_devise_fr = os.getenv('NATIONAL_DEVISE_FR')
national_devise_en = os.getenv('NATIONAL_DEVISE_EN')
school_republic_fr = os.getenv('SCHOOL_REPUBLIC_FR')
school_republic_en = os.getenv('SCHOOL_REPUBLIC_EN')
logo_url = os.getenv('LOGO_URL')

supabase_client = create_client(url, key)

# supabase_client.auth.sign_in_with_password(
#     {"email": 'principal@mail.com', 'password': '123456'}
# )
#
# student_averages = supabase_client.table("sequence_averages").select("*").eq('sequence', "sequence 2").execute()
# datas = student_averages.data
#
# moy_gen = 0
# sup = 0
# liste = []
#
# for row in datas:
#     if row['class_id'] == "c43f3cff-96a6-4d00-8c3f-10ac7a4393ac":
#         liste.append(row["value"])
#         if row['value'] >= 10:
#             sup += 1
#
# print(min(liste))
# print(max(liste))
# print(sup)


# file_path = "notes.xlsx"
# absolute_path = os.path.abspath(file_path)
# workbook = openpyxl.load_workbook(absolute_path)
# sheet = workbook.active
# valeurs = list(sheet.values)
# header = valeurs[0]
# valeurs.remove(header)
#
# for i, row in enumerate(valeurs):
#     supabase_client.table("notes").insert(
#         {
#             "year_id": row[0], "student_id": row[1], 'class_id': row[2], "sequence": row[3], "subject_id": row[4],
#             "value": row[5], "coefficient": row[6], "author": row[7]
#         }
#     ).execute()
#     print(i + 1)
#
# resp = supabase_client.table('sequence_averages').select('*, classes(code)').execute()
# tle: list = []
#
# for item in resp.data:
#     if item['classes']['code'] == '3e ALL 2':
#         print(f"class_id: {item['class_id']}")
#         print(f"year_id: {item['year_id']}")
#         dico: dict = {}
#         for key in item.keys():
#             dico[key] = item[key]
#
#         tle.append(dico)
#
# print(f"longueur {len(tle)}")
#
# average = 0
# list_value = []
# nb_sup_10 = 0
#
# for item in tle:
#     if item['value'] >= 10:
#         nb_sup_10 += 1
#
#     average += item['value']
#     list_value.append(item['value'])
#
# moy_gen = average / len(tle)
# print(f"moygen: {moy_gen}")
#
# print(f"nb > 10 {nb_sup_10}")
# print(f'notemin {min(list_value)}')
# print(f'notemax {max(list_value)}')
# print(f'taux de réussite: {nb_sup_10 * 100 / len(tle)}')
#
#
#
#
#
#
#
#
#
