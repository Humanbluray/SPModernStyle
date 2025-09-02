import flet as ft
from components.item_menu import ItemMenu
from utils.couleurs import *
from translations.translations import languages
from views.tabs.students import Students
from views.tabs.classes import Classes
from views.tabs.teachers import Teachers


roles = {
    'board' : {'admin': True, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
    'students' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'classes' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': False, 'économe': False, 'professeur': False},
    'teachers' : {'admin': True, 'principal': True, 'préfet': False, 'secrétaire': True, 'économe': False, 'professeur': False},
    'timetable' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'school_fees' : {'admin': False, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': True, 'professeur': False},
    'notes' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'report_book' : {'admin': True, 'principal': True, 'préfet': True, 'secrétaire': True, 'économe': True, 'professeur': True},
    'users' : {'admin': True, 'principal': False, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
    'years' : {'admin': False, 'principal': True, 'préfet': False, 'secrétaire': False, 'économe': False, 'professeur': False},
}

class NavBar(ft.Column):
    def __init__(self, cp: object):
        super().__init__(
            expand=True
        )
        # container parent _____________________________________________________
        self.cp = cp
        lang = self.cp.language
        role = self.cp.page.client_storage.get('role')

        # items ____________________________________________________________________________
        self.board = ItemMenu(languages[lang]['menu board'], ft.Icons.DASHBOARD_OUTLINED, ft.Icons.DASHBOARD, roles['board'][role])
        self.students = ItemMenu(languages[lang]['menu students'], ft.Icons.SWITCH_ACCOUNT_OUTLINED, ft.Icons.SWITCH_ACCOUNT, roles['students'][role])
        self.classes = ItemMenu(languages[lang]['menu classes'], ft.Icons.ROOFING_OUTLINED, ft.Icons.ROOFING, roles['classes'][role])
        self.teachers = ItemMenu(languages[lang]['menu teachers'],  ft.Icons.PERSON_OUTLINED, ft.Icons.PERSON, roles['teachers'][role])
        self.timetable = ItemMenu(languages[lang]['menu time table'], ft.Icons.EVENT_NOTE_OUTLINED, ft.Icons.EVENT_NOTE, roles['timetable'][role])
        self.school_fees = ItemMenu(languages[lang]['menu school fees'], ft.Icons.CURRENCY_EXCHANGE_OUTLINED, ft.Icons.CURRENCY_EXCHANGE, roles['school_fees'][role])
        self.notes = ItemMenu(languages[lang]['menu notes'], ft.Icons.CONTENT_COPY_OUTLINED, ft.Icons.CONTENT_COPY, roles['notes'][role])
        self.report_book = ItemMenu(languages[lang]['menu report book'], ft.Icons.RULE_FOLDER_OUTLINED, ft.Icons.RULE_FOLDER, roles['report_book'][role])
        self.users = ItemMenu(languages[lang]['menu users'], ft.Icons.SETTINGS_OUTLINED, ft.Icons.SETTINGS, roles['users'][role])
        self.years = ItemMenu(languages[lang]['menu academic years'],  ft.Icons.CALENDAR_MONTH_OUTLINED, ft.Icons.CALENDAR_MONTH, roles['years'][role])

        self.children = [
            self.board, self.students, self.classes, self.teachers, self.timetable,
            self.school_fees, self.notes, self.report_book, self.users, self.years
        ]

        for child in self.children:
            child.on_click = self.click_on_menu

        self.controls=[
            self.board, self.students, self.classes, self.teachers, self.timetable,
            self.school_fees,
            self.notes, self.report_book, self.users, self.years
        ]

    def click_on_menu(self, e):
        for child in self.children:
            child.set_is_clicked_false()
            child.is_clicked = False
            child.update()

        e.control.set_is_clicked_true()
        e.control.is_clicked = True
        e.control.update()

        self.cp.my_content.controls.clear()

        if e.control.name.value.lower() in (
                languages['en']['menu students'].lower(), languages['fr']['menu students'].lower()):
            self.cp.my_content.controls.append(Students(self.cp))
            self.cp.page.update()

        elif e.control.name.value.lower() in (
                languages['en']['menu classes'].lower(), languages['fr']['menu classes'].lower()):
            self.cp.my_content.controls.append(Classes(self.cp))
            self.cp.page.update()

        elif e.control.name.value.lower() in (
                languages['en']['menu teachers'].lower(), languages['fr']['menu teachers'].lower()):
            self.cp.my_content.controls.append(Teachers(self.cp))
            self.cp.page.update()

        else:
            print("ok")





