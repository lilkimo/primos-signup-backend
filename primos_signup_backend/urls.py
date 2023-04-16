from typing import List
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema

from requests import Session
from bs4 import BeautifulSoup

api = NinjaAPI()

class Detail(Schema):
    detail: str

class Credentials(Schema):
    login: str
    server: str
    passwd: str

class Schedule(Schema):
    schedule: List[bool]

@api.post("/schedule", response={200: Schedule, 400: Detail})
def get_schedule(_, payload: Credentials):
    schedule = [[], [], [], [], [], [], []]
    with Session() as session:
        # Accedemos al SIGA
        response = session.post('https://siga.usm.cl/pag/valida_login.jsp', data=payload.dict())
        if 'error_ingreso_login.jsp' in response.text:
            return 400, {'detail': 'wrong user/password'}
        # Solicitamos el horario
        response = session.post('https://siga.usm.cl/pag/sistinsc/insc_horario_per_detalle.jsp', data={'periodo': '2023-1', 'tipo_inscripcion': 2})

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
            "schedule": [item for sublist in map(lambda block: block[:8], schedule[:5]) for item in sublist]
        }



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
