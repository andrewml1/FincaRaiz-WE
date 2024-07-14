import csv
import concurrent.futures
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from collections import namedtuple
from selenium.webdriver.common.by import By
from links import obtener_enlaces_totales

Oferta = namedtuple("Oferta", [
    "carac",
    "precio",
    "hab",
    "baños",
    "parqueaderos",
    "areaconstruida",
    "areaprivada",
    "estrato",
    "pison",
    "administracion",
    "coord",
    "barrio",
    "antiguedad",
    "enlace",
])

lista_ofertas = []

enlaces = obtener_enlaces_totales(15)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")


def procesar_enlace(enlace):
    try:
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(enlace)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, "html.parser")

            script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
            json_data = json.loads(script_tag.string)

            property_data = json_data["props"]["pageProps"]["data"]
            technical_sheet = property_data.get("technicalSheet", [])

            # Extraer el nombre del barrio específico
            barrios = property_data["locations"]["neighbourhood"]
            barrio = barrios[2]["name"] if len(barrios) > 2 else None

            oferta_actual = {
                "carac": next((item["value"] for item in technical_sheet if item["field"] == "property_type_name"),
                              None),
                "precio": property_data["price"]["amount"],
                "hab": next((item["value"] for item in technical_sheet if item["field"] == "bedrooms"), None),
                "baños": next((item["value"] for item in technical_sheet if item["field"] == "bathrooms"), None),
                "parqueaderos": next((item["value"] for item in technical_sheet if item["field"] == "garage"), None),
                "areaconstruida": next((item["value"] for item in technical_sheet if item["field"] == "m2Built"), None),
                "areaprivada": next((item["value"] for item in technical_sheet if item["field"] == "m2Terrain"), None),
                "estrato": next((item["value"] for item in technical_sheet if item["field"] == "stratum"), None),
                "pison": next((item["value"] for item in technical_sheet if item["field"] == "floor"), None),
                "administracion": next((item["value"] for item in technical_sheet if item["field"] == "commonExpenses"),
                                       None),
                "coord": property_data["locations"]["location_point"],
                "barrio": barrio,
                "antiguedad": next((item["value"] for item in technical_sheet if item["field"] == "constructionYear"),
                                   None),
                "enlace": enlace,
            }

            lista_ofertas.append(Oferta(**oferta_actual))

    except Exception as e:
        print(f"Error en el enlace {enlace}: {str(e)}")


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(procesar_enlace, enlace) for enlace in enlaces]

# Esperar a que todas las tareas se completen
concurrent.futures.wait(futures)

# Guardar los datos en un archivo CSV
csv_filename = "ofertas.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(Oferta._fields)
    csv_writer.writerows(lista_ofertas)

print(f"Datos guardados en {csv_filename}")