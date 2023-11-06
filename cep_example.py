import logging
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pymysql.cursors
import datetime

# Função para inicializar o driver
def iniciar_driver():
    driver = webdriver.Firefox()
    driver.get("https://www2.correios.com.br/sistemas/precosprazos/restricaoentrega/")
    return driver

# Função para criar uma conexão com o banco de dados
def criar_conexao():
    return pymysql.connect(
        host='your_host',
        user='your_user',
        database='your_database',
        password='your_password',
        cursorclass=pymysql.cursors.DictCursor
    )

# Função para atualizar o status no banco de dados
def atualizar_status_no_banco(cep, status, conexao, cursor):
    try:
        status = status[:255]
        comando = f'UPDATE cep_status SET status = %s WHERE cep = %s'
        cursor.execute(comando, (status, cep))
        conexao.commit()
    except Exception as e:
        logger.error(f"Erro ao atualizar status no banco de dados para o CEP {cep}: {str(e)}")

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


conexao = criar_conexao()
cursor = conexao.cursor()

comando = f'SELECT cep FROM cep_status WHERE status IS NULL'
cursor.execute(comando)
ceps = cursor.fetchall()

contador = 676673
contador_sessao = 1

contador_ceps = 0  # Inicialize o contador de CEPs processados
driver = iniciar_driver()  # Inicialize o driver

for cep_info in ceps:
    cep = cep_info['cep']

    try:
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
            msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/2/div/div/div[2]/div[2]/div[2]/table[1]/tbody/tr/td/div/div')
        
        except NoSuchElementException:
            sleep(0.5)
            msg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/2/div/div/div[2]/div[2]/div[2]/div/div')
        
        except Exception as e:
            erro = str(e)
            erro = erro[55:]
            atualizar_status_no_banco(cep, erro, conexao, cursor)
            continue    

        msg_text = msg.text[:255]
        atualizar_status_no_banco(cep, msg_text, conexao, cursor)

        contador_ceps += 1  # Incrementa o contador de CEPs processados

        if contador_ceps == 500:  # Se 500 CEPs foram processados, reinicie o driver
            driver.quit()  # Fecha o driver atual
            contador_ceps = 0  # Reinicializa o contador
            driver = iniciar_driver()  # Inicializa um novo driver
        else:
            try:
                nova = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/2/div/div/div[2]/div[2]/div[2]/table[2]/tbody/tr[6]/td/input')
                nova.click()
            except NoSuchElementException:
                driver.quit()  # Fecha o driver atual
                driver = iniciar_driver()

        if "This site can't be reached" in driver.page_source:
            logger.info("A conexão com o site caiu. Recarregando a página.")
            driver.quit()
            driver = iniciar_driver()

    except Exception as e:
        logger.error(f"Erro ao processar o CEP {cep}: {str(e)}")

# Feche o driver quando terminar
driver.quit()
cursor.close()
conexao.close()
