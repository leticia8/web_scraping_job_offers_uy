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


def obtain_details(anuncio):
    detalles = anuncio.find_all('div', class_='col-sm-12 detalles')
    for detalle in detalles:
        lug_y_ar = detalle.find_all('h2')
        lugar = lug_y_ar[0].text
        if (len(lug_y_ar) > 1):
            area = lug_y_ar[1].text
        else:
            area = None
        cant_p_y_jor = detalle.find_all('span')
        # print(cant_p_y_jor)
        cant_puestos = None
        jornada_laboral = None
        if (len(cant_p_y_jor) == 1):
            jornada_laboral = cant_p_y_jor[0].text
        if (len(cant_p_y_jor) > 1):
            cant_puestos = cant_p_y_jor[0].text
            jornada_laboral = cant_p_y_jor[1].text
    return lugar, area, cant_puestos, jornada_laboral


def obtain_description(anuncio):
    descripcion = anuncio.find('div', class_='col-md-12 descripcion-texto').p
    for e in descripcion.findAll('br'):
        e.replace_with(' ')
    if (descripcion is not None):
        descripcion = descripcion.text
    return descripcion


def obtain_index(where_to_look, string_to_look):
    return where_to_look.find(string_to_look)


def depure_text(what_to_depure, string_to_delete):
    if (what_to_depure is not None):
        return what_to_depure.replace(string_to_delete, '').strip()


def obtain_time_salary(anuncio):
    otros_detalles = anuncio.find_all('div', class_='row oferta-contenido')
    salida = []
    area_tod = anuncio.find('div', class_='row oferta-contenido').find('div', class_='col-md-12').find('ul')
    area = area_tod.get_text().strip()
    # print(area)
    for un_det in otros_detalles:
        salida.append(clean(un_det.text) + ' ')
    niv_jer_y_area = salida[0]
    ind_nivel_jer = obtain_index(niv_jer_y_area, 'Nivel Jerárquico: ')
    ind_salario_nom = obtain_index(niv_jer_y_area, 'Salario Nominal: ')
    ind_horario = obtain_index(niv_jer_y_area, 'Horario: ')
    ind_area = obtain_index(niv_jer_y_area, 'Área: ')
    nivel_jerarquico, horario, salario_nom = None, None, None
    if (ind_nivel_jer != (-1)):
        if (ind_salario_nom != (-1)):
            nivel_jerarquico = niv_jer_y_area[:ind_salario_nom]
            if (ind_horario != (-1)):
                salario_nom = niv_jer_y_area[ind_salario_nom:ind_horario]
                horario = niv_jer_y_area[ind_horario:ind_area]
            else:
                salario_nom = niv_jer_y_area[ind_salario_nom:ind_area]
        else:
            if (ind_horario != (-1)):
                nivel_jerarquico = niv_jer_y_area[:ind_horario]
                horario = niv_jer_y_area[ind_horario:ind_area]
            else:
                nivel_jerarquico = niv_jer_y_area[:ind_area]
    nivel_jerarquico = depure_text(nivel_jerarquico, 'Nivel Jerárquico: ')
    salario_nom = depure_text(salario_nom, 'Salario Nominal:  ')
    horario = depure_text(horario, 'Horario: ')
    return salida, nivel_jerarquico, area, horario, salario_nom


def obtain_study_language(salida, anuncio):
    varios = salida[1]
    conocim_tod = anuncio.find_all('div', class_='row oferta-contenido')[1].find('div', class_='col-md-12').find('ul')
    conocimiento = None
    if (conocim_tod is not None):
        conocimiento = conocim_tod.get_text().strip()
    ind_idioma = obtain_index(varios, "Idiomas: ")
    ind_est_min = obtain_index(varios, "Estudio Mínimo Necesario: ")
    ind_area_est = obtain_index(varios, "Áreas de estudio: ")
    area_est, idiomas = None, None
    if(ind_area_est != (-1) and ind_idioma == (-1)):
        area_est_tod = anuncio.find_all(
            'div', class_='row oferta-contenido')[1].find('div', class_='col-md-12').find_all('ul')[1]
        area_est = area_est_tod.text.strip()
    elif (ind_area_est != (-1) and ind_idioma != (-1)):
        area_est_tod = anuncio.find_all(
            'div', class_='row oferta-contenido')[1].find('div', class_='col-md-12').find_all('ul')[2]
        idiomas = anuncio.find_all(
            'div', class_='row oferta-contenido')[1].find('div', class_='col-md-12').find_all('ul')[1]
        idiomas = idiomas.text.strip()
    # print(idioma_tod)
    ind_sexo = obtain_index(varios, "Sexo: ")
    niv_edu, sexo = None, None
    if (ind_area_est != (-1)):
        if(ind_sexo != (-1)):
            sexo = varios[ind_sexo:]
        if(ind_est_min != (-1)):
            niv_edu = varios[ind_est_min:ind_area_est]
    else:
        if(ind_est_min != (-1)):
            if(ind_sexo != (-1)):
                niv_edu = varios[ind_est_min:ind_sexo]
                sexo = varios[ind_sexo:]
        else:
            if (ind_idioma == (-1)):
                if(ind_sexo != (-1)):
                    sexo = varios[ind_sexo:]
    niv_edu = depure_text(niv_edu, 'Estudio Mínimo Necesario: ')
    sexo = depure_text(sexo, 'Sexo: ')
    return conocimiento, idiomas, area_est, niv_edu, sexo


def main():
    row = [1]
    next_page = 'https://www.buscojobs.com.uy/ofertas'
    data_frame_anuncios = pd.DataFrame(columns=('titulo', 'empresa', 'tiempo', 'cant_puestos', 'puesto',
                                                'oferta_salarial', 'responsabilidades', 'funciones', 'requisitos', 'link', 'fecha_consulta', 'lugar', 'jornada_laboral'))
    num = 1
    while(num < 85):
        URLstart = next_page
        print(next_page)
        page = requests.get(URLstart)
        resultListado = BeautifulSoup(page.content, 'html.parser')
        link_anuncios = resultListado.find_all('div', class_='row result click destacada-listado')
        link_anuncios2 = resultListado.find_all('div', class_='row result click destacada')
        link_anuncios3 = resultListado.find_all('div', class_='row result click')
        conj_links = [link_anuncios, link_anuncios2, link_anuncios3]
        siguiente_pagina = resultListado.find('li', {'id': 'paginaSiguiente'})
        next_page = 'https://'+(siguiente_pagina.find('a')['href'])[2:]
        num2 = URLstart.split('/')[-1]
        if (num2 == 'ofertas'):
            num = 1
        else:
            num = int(num2)
        for cada_link in conj_links:
            for link in cada_link:
                tiempo = link.find('span', class_='pull-right')
                tiempo = tiempo.string
                URL_anuncio = link.a['href']
                URL_dep = 'https://www.'+URL_anuncio[6:]
                print(URL_dep)
                pag_anun = requests.get(URL_dep)
                anuncio = BeautifulSoup(pag_anun.content, 'html.parser')
                titulo = anuncio.find('h1', class_='oferta-title').text.strip()
                print(titulo)
                empresas = anuncio.find_all('div', class_='col-sm-12 no-padding-right')
                empresa = (empresas[1].text.strip())
                lugar, area, cant_puestos, jornada_laboral = obtain_details(anuncio)
                descripcion = obtain_description(anuncio)
                salida, nivel_jerarquico, area, horario, salario_nom = obtain_time_salary(anuncio)
                conocimiento, idiomas, area_est, niv_edu, sexo = obtain_study_language(salida, anuncio)
                values_to_add = {'link': URL_dep, 'puesto': None, 'fecha_consulta': fecha, 'area': area, 'titulo': titulo,
                                 'empresa': empresa, 'tiempo': tiempo, 'cant_puestos': cant_puestos, 'oferta_salarial': salario_nom, 'responsabilidades': descripcion,
                                 'funciones': None, 'requisitos': None, 'lugar': lugar, 'jornada_laboral': jornada_laboral,
                                 'conocimientos': conocimiento, 'idiomas': idiomas, 'area_estudio': area_est, 'nivel_educativo': niv_edu,
                                 'nivel_jerarquico': nivel_jerarquico, 'horario': horario, 'sexo': sexo, 'fuente': 'buscojobs'}
                row_to_add = pd.Series(values_to_add, name=row[0])
                data_frame_anuncios = data_frame_anuncios.append(row_to_add)
                row[0] += 1
                print("\n ###################### \n")
        print(data_frame_anuncios)
        data_frame_anuncios.to_csv(f"salida_ws_busco_jobs{fecha}.csv", mode='w')


if __name__ == "__main__":
    main()
