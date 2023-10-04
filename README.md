<h1>Web Scraping Site Correrios</h1>

<h3>Programa que verifica a restrição de CEPs no site dos Correrios: https://www2.correios.com.br/sistemas/precosprazos/restricaoentrega/ </h3>

<h2>Passo a passo para utilizar o programa</h2>

<h3>No Linux:</h3>
<h4>Bibliotecas para serem instaladas:<br>
- instalar o pip: sudo apt-get install python3-pip<br>
- pip install selenium pymysql beautifulsoup4 pandas<br>
- sudo apt update<br>
- sudo apt install firefox //Somente se não tiver o FireFox instalado no computador</h4>

<h3>No Windows:</h3>
<h4> Para fazer a instalação da versão mais recente do Python no Windows: https://www.python.org/downloads/windows/<br>
- pip install selenium pymysql beautifulsoup4 pandas</h4>

<h3>Observação</h3>
<h4>Após download do programa, copiar o arquivo cep_example.py e renomear para cep.py e colocar sua conexão de banco de dados</h4>

<h3>Para rodar o programa:</h3>
<h4>No Linux: python3 nome_do_programa</h4>
<h4>No Windows: python nome_do_programa</h4>