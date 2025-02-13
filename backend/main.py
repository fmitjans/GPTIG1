from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

import os
from dotenv import load_dotenv

import openai
import parameters as p

from url import encode_url

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def init_driver():
    if p.USING_FIREFOX:
        options = FirefoxOptions()
        options.headless = True
        options.add_argument("--headless") 
        options.add_argument("--no-sandbox") 
        service = Service(p.GECKODRIVER_LOCATION)
        driver = webdriver.Firefox(service=service, options=options)
    else:
        driver = webdriver.Chrome()
    
    return driver

def get_offers(search_params):
    search_params = json.loads(search_params)
    # Verificar el contenido
    print("search_params después de cargar JSON:")
    print(json.dumps(search_params, indent=2, ensure_ascii=False))

    searchKeyword = search_params["searchKeyword"]
    region = encode_url(search_params["region"])
    n_educativo = encode_url(search_params["nivelEducativo"])
    jornada_laboral = encode_url(search_params["jornadaLaboral"])
    fecha_publicacion = encode_url(search_params["fechaPublicacion"])

    # https://www.bne.cl/ofertas?mostrar=empleo
    # &textoLibre=
    # &idRegion=378
    # &idNivelEducacional=5
    # &idTipoJornada=9
    # &fechaIniPublicacion=22%2F11%2F2024
    # &numPaginaRecuperar=1&numResultadosPorPagina=10&clasificarYPaginar=true&totalOfertasActivas=6188
    url = f'https://www.bne.cl/ofertas?mostrar=empleo' 
    url += f'&textoLibre={searchKeyword}'
    url += f'&idRegion={region}'
    url += f'&idNivelEducacional={n_educativo}'
    url += f'&idTipoJornada={jornada_laboral}'
    url += f'&fechaIniPublicacion={fecha_publicacion}'
    url += f'&numPaginaRecuperar=1&numResultadosPorPagina=10&clasificarYPaginar=true&totalOfertasActivas=6188'
    print("URL:")
    print(url)
    print()

    driver = init_driver()
        
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "row.margenVerticales.resultadoOfertas.noMargingLaterales.seccionOferta"))
    )
    no_results_message = "No se encontraron resultados para su búsqueda."
    
    try:
        no_results_element = driver.find_element(By.XPATH, "//div[@id='paginaOfertas']/h3")
        if no_results_element:
            WebDriverWait(driver, 15).until(
                EC.text_to_be_present_in_element((By.XPATH, "//div[@id='paginaOfertas']/h3"), "No se encontraron resultados para su búsqueda.")
            )
            no_results_element = driver.find_element(By.XPATH, "//div[@id='paginaOfertas']/h3")
            if no_results_message in no_results_element.text:
                print("No se encontraron resultados.")
                driver.close()
                return json.dumps([])  # O retorna un JSON vacío, por ejemplo: json.dumps([])
            else:
                print("No se encontró el mensaje de 'No resultados'")
        
    except Exception as e:
        print("No se encontró el mensaje de 'No resultados', continuando con el scraping.")
    # Definir diccionarios para guardar resultados
    resultados = [dict() for i in range(5)]
    # Campos para scrapping
    tag_off = "row.margenVerticales.resultadoOfertas.noMargingLaterales.seccionOferta"
    offers = driver.find_elements(By.CLASS_NAME, tag_off)
    tags = ["datosEmpresaOferta", "tituloOferta", "descripcionOferta", "fechaOferta"]
    
    n_offers = min(len(offers), 5)
    resultados = [dict() for i in range(n_offers)]
    for i in range(n_offers):
        resultados[i]["index"] = i
        for tag in tags:
            # Encontrar elementos con la clase tag
            element = offers[i].find_element(By.CLASS_NAME, tag)
            text = element.get_attribute('textContent').strip()
            # Texto de BNE viene con espacios en blanco
            resultados[i][tag] = text.split("     ")[0].strip()
            if (tag == "tituloOferta"):
                link = element.find_element(By.TAG_NAME, "a") #get_attribute('href')
                resultados[i]['link'] = link.get_attribute('href')
            elif (tag == "datosEmpresaOferta"):
                resultados[i]['ubicacionOferta'] = text.split("     ")[-1].strip()


    resultados_json_str = json.dumps(resultados, indent=2, ensure_ascii= False)

    driver.close()

    return resultados_json_str

def get_details(offer_code):
    url = f"https://www.bne.cl/oferta/{offer_code}"
    driver = init_driver()    
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'nombreOferta'))
    )

    data = dict()
    titulo      = driver.find_element(By.ID, 'nombreOferta')
    panels      = driver.find_elements(By.CLASS_NAME, 'panel-body')
    contact     = panels[1].find_elements(By.CLASS_NAME, 'col-sm-12')
    description = panels[2].find_element(By.CLASS_NAME, 'col-sm-12')
    specs       = panels[2].find_elements(By.CLASS_NAME, 'col-sm-3')
    dates       = panels[2].find_elements(By.TAG_NAME, 'span')[1:3]
    level       = panels[3].find_element(By.CLASS_NAME, 'col-sm-8')
    experience  = panels[3].find_element(By.CLASS_NAME, 'col-sm-4')
    others      = panels[4].find_elements(By.CLASS_NAME, 'col-sm-6')

    long_title      = titulo.get_attribute('textContent').strip()
    data['titulo']  = ' '.join(long_title.split()[:10])
    data['empresa']     = contact[0].get_attribute('textContent').split(sep=':')[-1].strip()
    data['actividad']   = contact[1].get_attribute('textContent').split(sep=':')[-1].strip()
    data['descripcion'] = description.get_attribute('textContent').strip()
    data['ubicacion']   = specs[0].get_attribute('textContent').strip()
    data['remuneracion']= specs[1].get_attribute('textContent').strip()
    data['jornada']     = specs[2].get_attribute('textContent').strip()
    data['nivel']       = level.get_attribute('textContent').split(sep=':')[-1].strip()
    data['experiencia'] = experience.get_attribute('textContent').split(sep=':')[-1].strip()
    data['contrato']    = others[0].get_attribute('textContent').split(sep=':')[-1].strip()
    data['cargo']       = others[1].get_attribute('textContent').split(sep=':')[-1].strip()
    data['origen']      = others[2].get_attribute('textContent').split(sep=':')[-1].strip()
    data['practica']    = others[3].get_attribute('textContent').split(sep=':')[-1].strip()
    data['fecha']       = dates[0].get_attribute('textContent').strip() # "10 de noviembre, 2024"
    data['expiracion']  = dates[1].get_attribute('textContent').strip()
    print(data)
    driver.close()
    return data


def generar_correo_openai(oferta):
    prompt = f"""
    Genera un correo formal siguiendo el formato AIDA para postularme a la siguiente oferta de trabajo:

    - Empresa: {oferta['empresa']}
    - Título del puesto: {oferta['titulo']}
    - Descripción del puesto: {oferta['descripcion']}

    Estructura del correo (AIDA):
    1. **Atención**: Captura la atención del reclutador de forma atractiva.
    2. **Interés**: Desarrolla el interés destacando cómo mis habilidades y experiencia se alinean con la oferta de trabajo.
    3. **Deseo**: Genera deseo mostrando cómo mi contribución puede beneficiar a la empresa.
    4. **Acción**: Termina con una llamada a la acción, como expresar mi disposición para una entrevista.

    Mi nombre es [mi nombre] y tengo experiencia relevante en este sector. Por favor, utiliza un tono profesional y cortés, y sigue la estructura AIDA al escribir el correo.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que genera correos formales siguiendo la estructura AIDA."},
            {"role": "user", "content": prompt}
        ]
    )

    # Obtener el texto generado
    correo_generado = response['choices'][0]['message']['content'].strip()
    return correo_generado



if __name__ == '__main__':
    codigo = '2024-107738'
    data = get_details(codigo)
    print(data)
    #for i in data.items():
    #    print(i)
