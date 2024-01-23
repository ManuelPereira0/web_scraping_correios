# Web Scraping Site Correrios

## Programa que verifica a restrição de CEPs no site dos Correrios: https://www2.correios.com.br/sistemas/precosprazos/restricaoentrega/

# Passo a passo para utilizar o programa

## Configurar DB
> Atualizar as informações abaixo para o seu DB
```python
host='seu host',
user='seu user',
database='seu database',
password='sua password',
```

### No Linux
Bibliotecas para serem instaladas:
- instalar o pip: sudo apt-get install python3-pip
- pip install selenium 
- pip install pymysql 
- pip install bs4 
- sudo apt update
- sudo apt install firefox 
> Somente se não tiver o FireFox instalado no computador

### No Windows
Para fazer a instalação da versão mais recente do Python no Windows: https://www.python.org/downloads/windows/
- pip install selenium 
- pip install pymysql 
- pip install bs4 

### Para rodar o programa
> No Linux: python3 nome_do_programa
> No Windows: python nome_do_programa<