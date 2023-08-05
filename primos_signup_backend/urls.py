from typing import List

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema

from primos_signup_backend.models import *
from primos_signup_backend import utils

from requests import Session
from bs4 import BeautifulSoup

api = NinjaAPI()

class Schedule(Schema):
    schedule: List[bool]

class Schedules(Schema):
    bussy_schedule: List[bool]
    desire_schedule: List[bool]

class Detail(Schema):
    detail: str

class Credentials(Schema):
    login: str
    server: str
    passwd: str

class RegisterForm(Schema):
    mail: str
    name: str
    rol: int | str
    nick: str
    bussy_schedule: List[bool]
    desire_schedule: List[bool]

@api.post('/schedule', response={200: Schedule, 400: Detail})
def get_siga_schedule(_, payload: Credentials):
    schedule = [[], [], [], [], [], [], []]
    with Session() as session:
        # Accedemos al SIGA
        response = session.post('https://siga.usm.cl/pag/valida_login.jsp', data=payload.dict())
        if 'error_ingreso_login.jsp' in response.text:
            return 400, {'detail': 'wrong user/password'}
        
        # Solicitamos el horario
        response = session.post('https://siga.usm.cl/pag/sistinsc/insc_horario_per_detalle.jsp', data={'periodo': '2023-2', 'tipo_inscripcion': 2})

        # Scrapping
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = iter(soup.find('table', class_='letra8').findChildren('tr', recursive=False))
        next(rows)
        for row in rows:
            blocks = row.findChild('td', recursive=False).findChildren('td', recursive=False)
            for i, block in enumerate(blocks):
                activity = block.select_one('td > table > tr > td')
                schedule[i].append(activity.has_attr('onmouseover'))

        return 200, {
            'schedule': [item for sublist in map(lambda block: block[:utils.num_blocks], schedule[:5]) for item in sublist]
        }

@api.get('/schedule', response={200: Schedules})
def get_registered_schedule(_, rol: int):
    try:
        primo = Primo.objects.get(rol=rol)
        return 200, {
            'bussy_schedule': utils.unparse_schedule(primo.bussy_schedule),
            'desire_schedule': utils.unparse_schedule(primo.desire_schedule),
        }
    except Primo.DoesNotExist:
        return 200, {f'{schedule}_schedule': [False]*5*utils.num_blocks for schedule in ('bussy', 'desire')}

@api.post('/register', response={200: None, 400: Detail})
def submit(_, payload: RegisterForm):
    if (len(payload.bussy_schedule) != 40 or len(payload.desire_schedule) != 40):
        return 400, {'detail': 'schedule arrays must have 40 items each'}
    
    transformations = {
        'bussy_schedule': utils.parse_schedule(payload.bussy_schedule),
        'desire_schedule': utils.parse_schedule(payload.desire_schedule),
    }
    Primo.objects.update_or_create(rol=str(payload.rol), defaults=payload.dict() | transformations)

    return 200, None

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
