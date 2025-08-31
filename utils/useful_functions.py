def format_number(n):
    if n >= 1_000_000:
        value = n / 1_000_000
        suffix = "M"
    elif n >= 1_000:
        value = n / 1_000
        suffix = "K"
    else:
        return str(n)

    # Si la valeur est entière, on affiche sans virgule
    if value.is_integer():
        return f"{int(value)}{suffix}"
    else:
        return f"{value:.1f}{suffix}"


def add_separator(number):
    """
    Used to add a thousand separator in a number
    :param number:
    :return new number with separator:
    """
    number = str(number)[::-1]
    result = ""
    for i, index in enumerate(number, 1):
        formatted_number = index + " ," if i % 3 == 0 and i != len(number) else index
        result += formatted_number

    return result[::-1]


def get_rating(my_note: float):
    if float(my_note) < 10:
        rating = "D"
    elif 10 <= float(my_note) < 12:
        rating = 'C'

    elif 12 <= float(my_note) < 14:
        rating = 'C+'

    elif 14 <= float(my_note) < 15:
        rating = 'B'

    elif 15 <= float(my_note) < 16:
        rating = 'B+'

    elif 16 <= float(my_note) < 18:
        rating = "A"

    else:
        rating = 'A+'

    return rating


def write_number(n):
    if n == int(n):
        return int(n)
    else:
        return f"{n:.2f}"


def convertir_date(date_str):
    """
    Convertit une date du format 'aaaa/mm/jj' en 'jj/mm/aaaa'.

    Exemple :
    convertir_date('2025/08/21') -> '21/08/2025'
    """
    annee, mois, jour = date_str.split('-')
    return f"{jour}/{mois}/{annee}"



