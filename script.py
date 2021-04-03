#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def raspar_tela(url):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
   
    driver.get(url)
    page = driver.page_source
    soup_lxml = BeautifulSoup(page, 'lxml')
    driver.quit()
    
    return soup_lxml


# In[ ]:


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


# In[ ]:


def salvar_arquivos(gerados):

    with open('exame_v0.tex', 'w') as file:  # Use file to refer to the file object
        file.write(gerados[0])

    with open('asw_key_v0.tex', 'w') as file:  # Use file to refer to the file object
        file.write(gerados[1])


# In[ ]:

import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver

def main():
    url = "https://mlapshin.com/index.php/scrum-quizzes/po-learning-mode"
    lxml = raspar_tela(url)
    ger = gerar_exame(lxml)
    salvar_arquivos(ger)

if __name__ == "__main__":
    main()
    os.system("pdflatex pspo_q1.tex")
    os.system("rm -rf asw_key_v0.tex exame_v0.tex *.aux *.log")
