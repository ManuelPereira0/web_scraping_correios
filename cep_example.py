import logging
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import csv
import re
import pymysql.cursors
import datetime
import sys

# Função para inicializar o driver
def iniciar_driver():
    driver = webdriver.Firefox()
    driver.get("https://www2.correios.com.br/sistemas/precosprazos/restricaoentrega/")
    return driver

conexao = pymysql.connect(
    host='your_host',
    user='your_user',
    database='your_database',
    password='your_password',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conexao.cursor()

comando = f'select cep from cep_status WHERE status is null'
cursor.execute(comando)
ceps = cursor.fetchall()

contador = 124942
contador_sessao = 0

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

contador_ceps = 0  # Inicialize o contador de CEPs processados
driver = iniciar_driver()  # Inicialize o driver

for cep in ceps:
    try:
        cep = cep['cep']

        data_hora_atual = datetime.datetime.now()
        data_hora_formada = data_hora_atual.strftime('%Y-%m-%d %H:%M:%S')

        print(f'{cep} , {data_hora_formada} , Nº{contador} e Nº{contador_sessao}')
        contador += 1
        contador_sessao += 1

        sleep(1)
        
        servico = Select(driver.find_element(By.XPATH, '//*[@id="servico"]'))
        servico.select_by_value('04510')
        
        origem = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/form/span[2]/label/input')
        origem.clear()  # Limpe qualquer texto existente
        origem.send_keys(cep)
        
        destino = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/form/span[3]/label/input')
        destino.clear()  # Limpe qualquer texto existente
        destino.send_keys(cep)

        pesquisa = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/form/div[2]/button')
            
        if pesquisa:
            sleep(0.3)
            pesquisa.click()
        else:
            driver.quit()  # Fecha o driver atual
            driver = iniciar_driver()
        
        # Aguarde até que a mensagem de resultado seja exibida
        try:
            sleep(0.5)
            msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table[1]/tbody/tr/td/div/div')        

        except NoSuchElementException:
            sleep(0.5)
            msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div/div')
        
        except NoSuchElementException:
            driver.quit()
            driver = iniciar_driver()
            
        except Exception as e:
            logger.error(f"Erro ao esperar pela mensagem de resultado: {e}")
            erro = str(sys.exc_info())  # Obtém a mensagem de erro atual
            erro = erro[:255]  # Limita o comprimento da mensagem a 255 caracteres (como no seu código original)
            
            atualizar_erro = f'UPDATE cep_status SET status = "Erro com o CEP" WHERE cep = "{cep}"'
            cursor.execute(atualizar_erro)
            conexao.commit() 
            
            continue  # Pule para o próximo CEP se a mensagem não for encontrada

        msg = msg.text[:255]
        atualizar = f'UPDATE cep_status SET status = "{msg}" WHERE cep = "{cep}"'
        cursor.execute(atualizar)
        conexao.commit() 

        contador_ceps += 1  # Incrementa o contador de CEPs processados

        if contador_ceps == 500:  # Se 500 CEPs foram processados, reinicie o driver
            driver.quit()  # Fecha o driver atual
            contador_ceps = 0  # Reinicializa o contador
            driver = iniciar_driver()  # Inicializa um novo driver
        else:
            try:
                nova = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table[2]/tbody/tr[6]/td/input')
                nova.click()
            except NoSuchElementException:
                driver.quit()  # Fecha o driver atual
                driver = iniciar_driver()

        if "This site can't be reached" in driver.page_source:
            logger.info("A conexão com o site caiu. Recarregando a página.")
            driver.quit()
            driver = iniciar_driver()
    except:
        driver.quit()
        driver = iniciar_driver()
        
# Feche o driver quando terminar
driver.quit()
cursor.close()
conexao.close()
