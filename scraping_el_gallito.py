import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
from datetime import date
os.chdir('/home/leticia/Desktop')

fecha = date.today()


def clean(string_to_clean):
    final_string = string_to_clean.strip().replace(
        '\r', '').replace('\n', '').replace('\t', '')
    return final_string


def obtain_attributes(results, tag, class_name, area_limp, row, data_frame_anuncios):
    links = results.find_all(tag, class_=class_name, href=True)
    for link in links:
        puesto = link.find_all('span', class_='link-post')[1].text
        comURL = link['href']
        baseURL = "https://trabajo.gallito.com.uy"
        longURL = baseURL+comURL
        page2 = requests.get(longURL)
        soup2 = BeautifulSoup(page2.content, 'html.parser')
        results2 = soup2.find('div', class_='col-xs-12 col-sm-8 col-md-8 spb specialImgRight')
        titulo = results2.find('h1').text.strip()
        empresa = results2.find('div', class_='subtitle-puesto').text
        tiempo = clean(results2.find_all('span', class_='time-text')[0].text)
        cant_puestos = clean(results2.find_all('div', class_='span-ofertas')[0].text)
        largo_camp = (len(results2.find_all('div', class_='span-ofertas')))
        if (largo_camp > 1):
            oferta_salarial = clean(results2.find_all('div', class_='span-ofertas')[1].text)
        else:
            oferta_salarial = ''
        largo_camp2 = (len(soup2.find_all('div',  class_='cuadro-aviso')))
        responsabilidades = clean(soup2.find_all('div', class_='cuadro-aviso-text')[0].text)
        funciones = clean(soup2.find_all('div', class_='cuadro-aviso-text')[1].text)
        if (largo_camp2 > 2):
            requisitos = clean(soup2.find_all('div', class_='cuadro-aviso-text')[2].text)
        else:
            requisitos = ''
        values_to_add = {'link': longURL, 'puesto': puesto, 'fecha_consulta': fecha, 'area': area_limp, 'titulo': titulo, 'empresa': empresa, 'tiempo': tiempo,
                         'cant_puestos': cant_puestos, 'oferta_salarial': oferta_salarial, 'responsabilidades': responsabilidades, 'funciones': funciones, 'requisitos': requisitos,
                         'fuente': 'el_gallito'}
        row_to_add = pd.Series(values_to_add, name=row[0])
        data_frame_anuncios = data_frame_anuncios.append(row_to_add)
        row[0] += 1
    return data_frame_anuncios, row


def clean_tildes(area):
    return area.lower().replace(' ', '').replace('í', 'i').replace(
        'ó', 'o').replace('á', 'a').replace('é', 'e').replace('ú', 'u')


def obtain_max(paginas):
    maximo = 0
    for pag in paginas:
        if (pag.text != '...'):
            number = int(pag.text)
            if (number > maximo):
                maximo = number
    return maximo


def main():
    row = [1]
    URLstart = 'https://trabajo.gallito.com.uy/'
    URLshort = 'https://trabajo.gallito.com.uy/buscar/areas/'
    page = requests.get(URLstart)
    resultFromArea = BeautifulSoup(page.content, 'html.parser')
    data_frame_anuncios = pd.DataFrame(columns=('titulo', 'empresa', 'tiempo', 'cant_puestos', 'puesto',
                                                'oferta_salarial', 'responsabilidades', 'funciones', 'requisitos', 'link', 'fecha_consulta'))
    areas = resultFromArea.find_all('h2', class_='span-icon-area-interes icon-pad-1')
    for area in areas:
        area_limp = clean_tildes(area.text)
        i = 1
        URL = URLshort+area_limp
        page = requests.get(URL)
        resPaginas = BeautifulSoup(page.content, 'html.parser')
        paginas = resPaginas.find_all('a', class_='paginate-gallito-number')
        maximo = obtain_max(paginas)
        for i in range(1, maximo+1):
            newURL = URL+"/page/"+str(i)
            print(newURL)
            page = requests.get(newURL)
            resPaginas = BeautifulSoup(page.content, 'html.parser')
            results = resPaginas.find('div', class_='contenedor-post-gallito col-xs-12 col-sm-9 col-md-9')
            data_frame_anuncios, row2 = obtain_attributes(
                results, 'a', 'post-cuadro row smB', area_limp, row, data_frame_anuncios)
            data_frame_anuncios, row3 = obtain_attributes(
                results, 'a', 'post-cuadro-web row smB', area_limp, row2, data_frame_anuncios)
            i += 1
            print(data_frame_anuncios)
        data_frame_anuncios.to_csv(f"salida_ws_gallito{fecha}.csv", mode='w')


if __name__ == "__main__":
    main()
