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

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conexao = pymysql.connect(
    host='your host',
    user='your user',
    database='your database',
    password='your password',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conexao.cursor()

comando = f'select cep from cep_status WHERE status is null limit 500'
cursor.execute(comando)
ceps = cursor.fetchall()

# Configuração do driver do Selenium
driver = webdriver.Firefox()
driver.get("https://www2.correios.com.br/sistemas/precosprazos/restricaoentrega/")

for cep in ceps:
    cep = cep['cep']
    print(cep)
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
    pesquisa.click()
    
    # Aguarde até que a mensagem de resultado seja exibida
    try:
        msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table[1]/tbody/tr/td/div/div')        
        sleep(0.5)

    except NoSuchElementException:
        msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div/div')
        sleep(0.5)
    
    except Exception as e:
        logger.error(f"Erro ao esperar pela mensagem de resultado: {e}")
        continue  # Pule para o próximo CEP se a mensagem não for encontrada

    atualizar = f'UPDATE cep_status SET status = "{msg.text}" WHERE cep = "{cep}"'
    cursor.execute(atualizar)
    conexao.commit() 

    sleep(1)

    nova = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/table[2]/tbody/tr[6]/td/input')
    nova.click()

# Feche o navegador quando terminar
driver.quit()

# Feche o cursor e a conexão após o loop
cursor.close()
conexao.close()
