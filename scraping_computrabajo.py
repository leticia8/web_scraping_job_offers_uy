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


def obtain_attributes(lista_por_area, URLstart, link_area, tag, class_name, row, data_frame_anuncios):
    pagina_todas_ofer = lista_por_area.find_all(tag, class_name)
    for una_ofer in pagina_todas_ofer:
        # link de cada oferta
        pag_ind = una_ofer['href']
        pag_final = URLstart+pag_ind
        para_datos = requests.get(pag_final)
        lista_titulos = BeautifulSoup(para_datos.content, 'html.parser')
        titulo = lista_titulos.find('h1', class_='m0').text
        print(titulo)
        oferta_salarial = clean(lista_titulos.find('p', class_='fc80 mt5').text).replace(' ', '')
        empresa_st = lista_titulos.find('a', {'id': 'urlverofertas'})
        if (empresa_st is not None):
            empresa = empresa_st.text.strip()
        else:
            empresa = None
        desc = lista_titulos.find('section', class_='boxWhite fl w_100 detail_of mb20 bWord')
        sals = desc.find_all('li')
        desc_y_req = []
        for sal in sals:
            desc_y_req.append(sal.text)
        requerimientos_list = desc_y_req
        desc_list = desc_y_req
        desc = requerimientos_list[0:requerimientos_list.index('Requerimientos')]
        descripcion = (' '.join(desc))
        req = desc_list[desc_list.index('Requerimientos'):]
        requisitos = (' '.join(req))
        areaLimp = link_area[1:].replace('-', ' ')
        values_to_add = {'link': pag_final, 'puesto': None, 'fecha_consulta': fecha, 'area': areaLimp, 'titulo': titulo, 'empresa': empresa, 'tiempo': None,
                         'cant_puestos': None, 'oferta_salarial': oferta_salarial, 'responsabilidades': descripcion, 'funciones': None, 'requisitos': requisitos, 'fuente': 'compu_trabajo'}
        row_to_add = pd.Series(values_to_add, name=row[0])
        data_frame_anuncios = data_frame_anuncios.append(row_to_add)
        row[0] += 1
    return data_frame_anuncios, row


def clean_tildes(area):
    return area.lower().replace(' ', '').replace('í', 'i').replace(
        'ó', 'o').replace('á', 'a').replace('é', 'e').replace('ú', 'u')


def main():
    row = [1]
    URLstart = 'https://www.computrabajo.com.uy'
    page = requests.get(URLstart)
    resultFromArea = BeautifulSoup(page.content, 'html.parser')
    data_frame_anuncios = pd.DataFrame(columns=('titulo', 'empresa', 'tiempo', 'cant_puestos', 'puesto',
                                                'oferta_salarial', 'responsabilidades', 'funciones', 'requisitos', 'link', 'fecha_consulta'))
    # acá se obtienen todas las áreas/categorías agregadas
    areas = resultFromArea.find_all('ul', {'id': 'content_3'})
    for area in areas:
        # para obtener el link del agregado anterior
        sals = (area.find_all('a'))
        es_primero = 0
        for sal in sals:
            print(URLstart+(sal['href']))
            link_area = sal['href']
            if (es_primero == 0):
                url_pagina_categoria = URLstart+(sal['href'])
                es_primero += 1
            if (link_area in ['/empleos-de-informatica-telecomunicaciones', '/empleos-de-contabilidad-finanzas', '/empleos-de-ingenieria', '/empleos-de-docencia', '/empleos-de-diseno-artes-graficas', '/empleos-de-investigacion-y-calidad']):
                es_primero = 0
            while(es_primero != 0):
                salida_pag = requests.get(url_pagina_categoria)
                lista_por_area = BeautifulSoup(salida_pag.content, 'html.parser')
                # para obtener las páginas activas y las pr
                siguiente_pagina = lista_por_area.find('li', class_='siguiente')
                if (siguiente_pagina is not None):
                    next_page = (siguiente_pagina.find('a', {'id': 'nextPage'}))
                if (next_page is not None):
                    link_next_page = next_page['href']
                else:
                    link_next_page = None
                # para obtener el link de un anuncio
                data_frame_anuncios, row = obtain_attributes(lista_por_area, URLstart, link_area, 'a', 'js-o-link', row, data_frame_anuncios)
                # recorre todas las ofertas de una página
                if (link_next_page is not None):
                    url_pagina_categoria = link_next_page
                else:
                    es_primero = 0
                    break
                print(data_frame_anuncios)
                data_frame_anuncios.to_csv(f"salida_ws_compu_trabajo{fecha}.csv", mode='w')


if __name__ == "__main__":
    main()
