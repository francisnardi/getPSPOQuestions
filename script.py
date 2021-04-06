#!/usr/bin/env python
# coding: utf-8

def raspar_tela(url):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=binary_path, options=options)
   
    driver.get(url)
    page = driver.page_source
    soup_lxml = BeautifulSoup(page, 'lxml')
    driver.quit()
    
    return soup_lxml

def gerar_exame(soup_lxml):

    wpProQuiz_question_text = soup_lxml.find_all(class_='wpProQuiz_question_text')
    wpProQuiz_questionList = soup_lxml.find_all(class_='wpProQuiz_questionList')
    wpProQuiz_correct = soup_lxml.find_all(class_='wpProQuiz_correct')
    pspo_document = '\\begin{enumerate}\n'
    answer_key = '\\begin{enumerate}\n'
    perguntas = [(e.text).strip() for e in wpProQuiz_question_text]
    alternativas = []
    alt = []
    respostas_1 = []
    respostas_2 = []
    rsp_1 = []
    rsp_2 = []

    for i in range(len(wpProQuiz_questionList)):
        pspo_document += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\t\\begin{todolist}\n"
        alt_raw = wpProQuiz_questionList[i].find_all('label')

        for j in range(len(alt_raw)):
            a = (alt_raw[j].text).strip()
            alt.append(a)
            pspo_document += "\t\t\\item " + a + "\n"
        alternativas.append(alt)
        pspo_document += "\t\\end{todolist}\n\n"
        alt = []

        answer_key += "\t% question " + str(i+1) + "\n\t\\item " + str(perguntas[i]) + "\n\n"
        rsp_raw1 = wpProQuiz_correct[i].find_all('p')
        rsp_raw2 = wpProQuiz_correct[i].find_all('li')

        r1 = (rsp_raw1[0].text).strip()    
        rsp_1.append(r1)
        answer_key += "\t" + r1 + "\n"
        respostas_1.append(rsp_1)
        rsp_1 = []

        if (rsp_raw2):
            answer_key += "\t\\begin{enumerate}\n"
            for k in range(len(rsp_raw2)):
                r2 = (rsp_raw2[k].text).strip()
                rsp_2.append(r2)
                answer_key += "\t\t\\item " + r2 + "\n"      
            answer_key += "\t\\end{enumerate}\n"
            respostas_2.append(rsp_2)
            rsp_2 = []
        else:
            respostas_2.append('')

    pspo_document += "\\end{enumerate}"
    answer_key += "\\end{enumerate}"

    prova = bytes(pspo_document, 'utf-8').decode('utf-8', 'ignore')
    gabarito = bytes(answer_key, 'utf-8').decode('utf-8', 'ignore')

    return [prova, gabarito]

def salvar_arquivos(gerados, gabarito):

    with open('exame_v0.tex', 'w') as file:  # Use file to refer to the file object
        file.write(gerados[0])

    with open('asw_key_v0.tex', 'w') as file:  # Use file to refer to the file object
        file.write(gerados[1])

    with open('shrt_asw_key_v0.tex', 'w') as file:  # Use file to refer to the file object
        file.write(gabarito)


def gerar_gabarito(lxml, arquivo_gabarito):
    with open(arquivo_gabarito) as json_file:
        data = json.load(json_file)

    wpProQuiz_question_text = lxml.find_all(class_='wpProQuiz_question_text')
    perguntas = [(e.text).strip() for e in wpProQuiz_question_text]
        
    letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    gabarito_resumido = ""
    count = 1

    gabarito_resumido += '\\begin{enumerate}\n'
    for element in data:
        gabarito_resumido += "\t% question " + str(count) + "\n\t\\item " + str(perguntas[count-1]) + "\n\n\t"
        gabarito_binario = data[element]['correct']
        for i in range(len(gabarito_binario)):
            if (gabarito_binario[i] == 1):
                gabarito_resumido += " " + str(letras[i]) + ", "
        gabarito_resumido = gabarito_resumido[:-2]
        gabarito_resumido += "\n\n"
        count += 1
    gabarito_resumido += '\\end{enumerate}'

    gbrs = bytes(gabarito_resumido, 'utf-8').decode('utf-8', 'ignore')

    return gbrs

import os
import time
import json
from chromedriver_py import binary_path
from bs4 import BeautifulSoup
from selenium import webdriver

def main():
    url = "https://mlapshin.com/index.php/scrum-quizzes/po-learning-mode"
    arquivo_gabarito = "gabarito.json"
    lxml = raspar_tela(url)
    ger = gerar_exame(lxml)
    gbrt = gerar_gabarito(lxml, arquivo_gabarito)
    salvar_arquivos(ger, gbrt)

if __name__ == "__main__":
    main()
    os.system("pdflatex v1.tex")
    os.system("pdflatex v2.tex")
    os.system("pdflatex v3.tex")
    os.system("rm -rf asw_key_v0.tex exame_v0.tex shrt_asw_key_v0.tex *.aux *.log *.fls *.fdb_*")