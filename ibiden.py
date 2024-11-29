from flask import Flask, request, render_template,render_template_string, redirect, url_for,  jsonify, flash, session, redirect
import requests
import logging
import pandas as pd
from io import StringIO
import json
import traceback
import plotly.graph_objects as go #Para Gráfico de casos reais e previsão
from markupsafe import Markup #Para o Mapa Brasil Capita
import folium
import psycopg2

from bs4 import BeautifulSoup
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'ibidenclima'  # Defina uma chave secreta para usar sessões

import psycopg2

class Conectar:
    def Conexao(self):
        try:
            conectar = psycopg2.connect(
                dbname="ibiden_banco",
                user="ibiden_banco_user",  
                password="xtWgaYBj1mzdfq6t7BTypWa6Y4iE3N9l",  
                host="dpg-cs99o4i3esus739cllo0-a.oregon-postgres.render.com",  
                port="5432"  # Porta padrão do PostgreSQL
            )
            print("Conectado ao banco de dados") 
            return conectar
        except Exception as e:
            print("Erro de conexão com o BD: ", e)
            raise

    @staticmethod
    def rota():
        return "login.html"

    def criar_tabela(self):
        conexao = self.Conexao()
        cursor = conexao.cursor()
        try:
            # Comando para criar a tabela
            criar_tabela_sql = """
            CREATE TABLE IF NOT EXISTS usuario (
                usu_id SERIAL PRIMARY KEY,
                usu_nome VARCHAR(150) NOT NULL,
                usu_email VARCHAR(150) NOT NULL UNIQUE,
               usu_pass VARCHAR(100) NOT NULL,
                estado INT NOT NULL CHECK (estado IN (0, 1)) -- 1 = ATIVO // 0 = INATIVO
            );
            """
            cursor.execute(criar_tabela_sql)
            conexao.commit()
            print("Tabela 'usuario' criada com sucesso")

            # Inserção de dados
            inserir_dados_sql = """
            INSERT INTO usuario (usu_nome, usu_email, usu_pass, estado) VALUES 
            ('Nathalia Viana', 'nathalia@gmail.com', '123456', 1),
            ('Nayra Alencar', 'nayra@gmail.com', '123456', 1),
            ('Thais Alencar', 'thais@gmail.com', '123456', 1)
            ON CONFLICT (usu_email) DO NOTHING;  -- Evitar duplicação
            """
            cursor.execute(inserir_dados_sql)
            conexao.commit()
            print("Dados inseridos na tabela 'usuario' com sucesso")

        except Exception as e:
            print("Erro ao criar tabela ou inserir dados: ", e)
            conexao.rollback()  # Desfaz as alterações em caso de erro
        finally:
            cursor.close()
            conexao.close()  # Fecha a conexão

# Uso
if __name__ == "__main__":
    conectar = Conectar()
    conectar.criar_tabela()


class Usuario(Conectar):
    # Método de login
    def login(self):
        conectar = super().Conexao()

        if "enviar" in request.form and request.form["enviar"] == "Acessar":
            email = request.form["usu_email"]
            password = request.form["usu_pass"]

            if not email or not password:
                return 2  # código para indicar que campos estão vazios
            else:
                with conectar.cursor() as cursor:
                    sql = "SELECT * FROM usuario WHERE usu_email=%s AND usu_pass=%s AND estado=1"
                    cursor.execute(sql, (email, password,))
                    resultado = cursor.fetchone()

                if resultado:
                    usu_id, usu_nome, usu_email, usu_pass, estado = resultado

                    session['logged_in'] = True
                    session['usu_email'] = usu_email  # Armazena o email na sessão
                    session['username'] = usu_nome
                    session['role'] = 'user'
                    
                    return "busca_clima.html"
                else:
                    return 1  # Credenciais inválidas

        return None
   
    # Método para registrar um novo usuário
    def registrar_usuario(self, nome, email, password):
        conectar = super().Conexao()
        try:
            # Verifica se o email já está registrado
            with conectar.cursor() as cursor:
                print(f"Verificando se o email {email} já está em uso.")  # Depuração
                sql_verificar = "SELECT * FROM usuario WHERE usu_email = %s"
                cursor.execute(sql_verificar, (email,))
                resultado = cursor.fetchone()

                if resultado:
                    print("Email já registrado.")  # Depuração
                    return False  # O email já está em uso
                else:
                    print("Inserindo novo usuário no banco de dados.")  # Depuração
                    # Insere o novo usuário no banco de dados
                    sql_inserir = """
                    INSERT INTO usuario (usu_nome, usu_email, usu_pass, estado)
                    VALUES (%s, %s, %s, 1)
                    RETURNING usu_id;
                    """
                    cursor.execute(sql_inserir, (nome, email, password,))
                    novo_usuario_id = cursor.fetchone()[0]
                    conectar.commit()
                    print(f"Usuário registrado com sucesso! ID: {novo_usuario_id}")  # Mensagem de sucesso
                    return True  # Registro bem-sucedido

        except Exception as e:
            print("Erro ao registrar o usuário:", e)  # Mensagem de erro
            conectar.rollback()  # Reverte a transação em caso de erro
            return False

    # Método para verificar o email
    def check_email(self, email):
        conectar = super().Conexao()
        with conectar.cursor() as cursor:
            sql_verificar = "SELECT * FROM usuario WHERE usu_email = %s"
            cursor.execute(sql_verificar, (email,))
            resultado = cursor.fetchone()
            return bool(resultado)

    # Método para verificar a senha
    def check_password(self, email, password):
        conectar = super().Conexao()
        with conectar.cursor() as cursor:
            sql_verificar = "SELECT * FROM usuario WHERE usu_email = %s AND usu_pass = %s"
            cursor.execute(sql_verificar, (email, password,))
            resultado = cursor.fetchone()
            return bool(resultado)

    # Método para atualizar a senha
    def update_password(self, email, new_password):
        conectar = super().Conexao()
        with conectar.cursor() as cursor:
            sql_update = "UPDATE usuario SET usu_pass = %s WHERE usu_email = %s"
            cursor.execute(sql_update, (new_password, email))
            conectar.commit()
            return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensagem = None
    if request.method == 'POST':
        if 'enviar' in request.form and request.form['enviar'] == 'Acessar':  
            usuario = Usuario()
            mensagem = usuario.login()
            if mensagem is None:
                mensagem = 'Credenciais inválidas. Por favor, tente novamente.'
            elif mensagem == 'busca_clima.html':
                return redirect('/busca_clima')
    return render_template('login.html', mensagem=mensagem)

@app.route('/registro', methods=["GET", "POST"])
def registro():
    mensagem = None  # Inicializa a variável mensagem
    if request.method == "POST":
        print("Formulário Recebido:", request.form)  
        if "enviar" in request.form and request.form["enviar"] == "Registrar-se no iBIDEN":  
            nome = request.form.get("usu_nome")  # Usando get para evitar UnboundLocalError
            email = request.form.get("usu_email")
            password = request.form.get("usu_pass")
            print(f"Nome: {nome}, Email: {email}, Senha: {password}")  # Debugging
            
            if not nome or not email or not password:
                mensagem = "Todos os campos são obrigatórios."
            else:
                usuario = Usuario()
                registro_ok = usuario.registrar_usuario(nome, email, password)
                if registro_ok:
                    mensagem = "Usuário registrado com sucesso!"
                else:
                    mensagem = "O email já está em uso. Tente outro."
    
    return render_template('registro.html', mensagem=mensagem)



#CLIMA&TEMPO

# Substitua 'YOUR_API_KEY' pela sua chave de API WeatherAPI.com
api_key = 'ea86ffcaee9a4737972222744230410'

# URL base da API
base_url = 'http://api.weatherapi.com/v1/current.json'


@app.route('/busca_clima')
def busca_clima():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('busca_clima.html', username=session['username'], umidade='', temperatura='', uv='', velocidade_vento='', cobertura_nuvens='', precipitacao='', pressao='', sensacao='', visibilidade='', condicao='')
    else:
        return redirect(url_for('login'))  # Redireciona para a página de login se o usuário não estiver logado ou não tiver a função de usuário


@app.route('/get_weather', methods=['POST'])
def get_weather():
    cidade = request.form['cidade']

    params = {
        'key': api_key,
        'q': cidade,
        'lr': 'lang_pt', 
        'hl': 'pt-BR', 
        'gl': 'br'
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})

            umidade = int(current.get('humidity', 0))
            temperatura = int(current.get('temp_c', 0))
            uv = int(current.get('uv', 0))
            velocidade_vento = int(current.get('wind_kph', 0))
            cobertura_nuvens = int(current.get('cloud', 0))
            precipitacao = current.get('precip_mm', 0)
            pressao = int(current.get('pressure_mb', 0))
            sensacao = int(current.get('feelslike_c', 0))
            visibilidade = int(current.get('vis_km', 0))
            condicao = current.get('condition', {})

            return render_template('clima_tempo.html', umidade=umidade, temperatura=temperatura, uv=uv, velocidade_vento=velocidade_vento, cobertura_nuvens=cobertura_nuvens, precipitacao=precipitacao, pressao=pressao, sensacao=sensacao, visibilidade=visibilidade, condicao=condicao)
        else:
            return render_template('clima_tempo.html', error="Nome inválido de pesquisa!"), 400

    except Exception as e:
        return render_template('clima_tempo.html', error=f"Erro ao buscar dados: {str(e)}"), 500

    

@app.route('/buscar_impactos')
def buscar_impactos():
    page = 1  # Defina o valor padrão para 'page' aqui
    total_pages = 1  # Defina o valor padrão para 'total_pages' aqui
    return render_template('buscar_impactos.html', page=page, total_pages=total_pages)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Se o formulário foi enviado, obtenha a consulta do formulário POST
        query = request.form.get('query', '')
    else:
        # Se a solicitação é GET, obtenha a consulta dos parâmetros da URL
        query = request.args.get('query', '')

    keywords = ["Mudanças Climáticas", "Efeito Estufa", "Aquecimento Global", "Impacto Ambiental", "Dengue", "Aedes Aegypti", ""]
    page = int(request.args.get('page', 1))  # Obtenha o número da página da URL
    results_per_page = 10  # Número de resultados por página
    start = (page - 1) * results_per_page + 1
    apiKey = 'AIzaSyC_fMenI7tZa1gp478-ymQL7PTKygyQ4fk'
    customSearchId = 'b5e1d48951aa44edf'

    query += ' ' + ' '.join(keywords)

    params = {
        'q': query,
        'lr': 'lang_pt',  # Filtrar os resultados para português
        'hl': 'pt-BR',  # Configurar o idioma da pesquisa como português do Brasil
        'gl': 'br',
        'cx': 'b5e1d48951aa44edf',
        'key': 'AIzaSyC_fMenI7tZa1gp478-ymQL7PTKygyQ4fk',
        'start': start
    }

    try:
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
        data = response.json()
        search_results = data.get('items', [])

        total_results = data.get('searchInformation', {}).get('totalResults', 0)

        total_pages = (int(total_results) - 1) // results_per_page + 1


        # Ajuste para usar a primeira palavra do parágrafo como título, se não houver título
        for result in search_results:
            if 'title' not in result and 'snippet' in result:
                snippet = result['snippet']
                soup = BeautifulSoup(snippet, 'html.parser')
                first_word = soup.get_text().split()[0]
                result['title'] = first_word

        # Filtrar resultados com títulos que não contenham a palavra "Untitled"
        filtered_results = [result for result in search_results if is_valid_result(result)]

        return render_template('resultado-pesquisa-impactos.html', results=filtered_results, page=page, total_pages=total_pages)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)

def is_valid_result(result):
        # Função auxiliar para verificar se um resultado é válido
        if 'title' in result:
            title = result['title'].strip().lower()
            return 'untitled' not in title
        return False


#GRÁFICOS DE PREVISÃO


# Função para obter os dados de uma capital específica
def get_data_for_capital(geocode):
    url = "https://info.dengue.mat.br/api/alertcity"
    disease = "dengue"
    format = "csv"
    ew_start = 1
    ew_end = 54
    ey_start = 2024
    ey_end = 2024

    params = (
        "&disease="
        + f"{disease}"
        + "&geocode="
        + f"{geocode}"
        + "&disease="
        + f"{disease}"
        + "&format="
        + f"{format}"
        + "&ew_start="
        + f"{ew_start}"
        + "&ew_end="
        + f"{ew_end}"
        + "&ey_start="
        + f"{ey_start}"
        + "&ey_end="
        + f"{ey_end}"
    )

    url_resp = "?".join([url, params])
    dados = pd.read_csv(url_resp, index_col='SE')
    return dados

# Dicionário de capitais e códigos geográficos
capitals_geocode = {
    'Acre': 1200401,
    'Alagoas': 2700300,
    'Amapá': 1600303,
    'Amazonas': 1302603,
    'Bahia': 2927408,
    'Ceará': 2304400,
    'Distrito Federal': 5300108,
    'Espírito Santo': 3201308,
    'Goiás': 5208707,
    'Maranhão': 2111300,
    'Mato Grosso': 5103403,
    'Mato Grosso do Sul': 5002704,
    'Minas Gerais': 3106200,
    'Pará': 1501402,
    'Paraíba': 2507507,
    'Paraná': 4106902,
    'Pernambuco': 2611606,
    'Piauí': 2211001,
    'Rio de Janeiro': 3304557,
    'Rio Grande do Norte': 2408102,
    'Rio Grande do Sul': 4314902,
    'Rondônia': 1100205,
    'Roraima': 1400100,
    'Santa Catarina': 4216602,
    'São Paulo': 3550308,
    'Sergipe': 2806701,
    'Tocantins': 1721000
}

@app.route('/casosgrafico', methods=['GET', 'POST'])
def casosgrafico():
    selected_capital = None
    plot_html = None

    if request.method == 'POST':
        capital = request.form['capital']
        geocode = capitals_geocode[capital]
        capital_data = get_data_for_capital(geocode)
        
        fig = go.Figure()

        # Adicionando casos estimados como linha
        fig.add_trace(go.Scatter(
            x=capital_data.index.map(lambda v: '%s' % (str(v)[-6:])),
            y=capital_data['casos_est'],
            mode='lines',
            name=f"{capital} - Previsão de Casos",
            marker_color='#1A5CF4',
            hovertemplate=(
                '%{text}' +
                '<br>' +
                '%{y:1f} - Casos Estimados' +
                '<extra></extra>'
            ),
            text="Semana: " + capital_data.index.map(lambda v: '{}'.format(str(v)[-2:])) +
                "<br>" +
                "Data: " + capital_data['data_iniSE'],
        ))

        # Adicionando casos reais como barras
        fig.add_trace(go.Bar(
            x=capital_data.index.map(lambda v: '%s' % (str(v)[-6:])),
            y=capital_data['casos'],
            name=f"{capital} - Casos Reais",
            marker_color='#FF5733',
            hovertemplate=(
                '%{text}' +
                '<br>' +
                '%{y:1f} Casos Reais' +
                '<extra></extra>'
            ),
            text="Semana: " + capital_data.index.map(lambda v: '{}'.format(str(v)[-2:])) +
                "<br>" +
                "Data: " + capital_data['data_iniSE'],
        ))

        fig.update_layout(
            title_text=f'Previsão de Casos X Casos Reais em {capital}',
            title_x=0.5,
            title_y=0.9,
            title_font=dict(
                size=20,
                color='black',
                family='Arial Black'  # Ou outra fonte que seja naturalmente em negrito
            ),
            yaxis=dict(
                title_text='Número de Casos',
                side='left',
                showline=False,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            xaxis=dict(
                title_text='Semanas Epidemológicas',
                showline=False,
                showgrid=True,
                showticklabels=True,
                autorange='reversed', 
                tickangle=-60,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            plot_bgcolor='rgb(255, 255, 255)',
            paper_bgcolor='rgb(245, 246, 249)',
            autosize=True,
        )

        plot_html = fig.to_html(full_html=False)

    return render_template('casosgrafico.html', capitals=capitals_geocode.keys(), plot_html=plot_html)


#MAPA CASOS DENGUE POR CAPITAL

# Lista de coordenadas das capitais brasileiras e seus códigos IBGE
capitais = {
    'Rio Branco': {'coords': [-9.97499, -67.8248977], 'geocode': 1200401},
    'Maceió': {'coords': [-9.6498487, -35.7292318], 'geocode': 2704302},
    'Macapá': {'coords': [0.034934, -51.0663888], 'geocode': 1600303},
    'Manaus': {'coords': [-3.1190275, -60.0217314], 'geocode': 1302603},
    'Salvador': {'coords': [-12.9714, -38.5014171], 'geocode': 2927408},
    'Fortaleza': {'coords': [-3.7172, -38.5266704], 'geocode': 2304400},
    'Brasília': {'coords': [-15.7801, -47.9292], 'geocode': 5300108},
    'Vitória': {'coords': [-20.3155, -40.3444], 'geocode': 3205309},
    'Goiânia': {'coords': [-16.6864, -49.2532], 'geocode': 5208707},
    'São Luís': {'coords': [-2.53073, -44.2968], 'geocode': 2111300},
    'Cuiabá': {'coords': [-15.601, -56.0979], 'geocode': 5103403},
    'Campo Grande': {'coords': [-20.4428, -54.6466], 'geocode': 5002704},
    'Belo Horizonte': {'coords': [-19.9281, -43.9389], 'geocode': 3106200},
    'Belém': {'coords': [-1.45502, -48.5044], 'geocode': 1501402},
    'João Pessoa': {'coords': [-7.11509, -34.876], 'geocode': 2507507},
    'Curitiba': {'coords': [-25.4278, -49.2731], 'geocode': 4106902},
    'Recife': {'coords': [-8.0476, -34.9011], 'geocode': 2611606},
    'Teresina': {'coords': [-5.08921, -42.815], 'geocode': 2211001},
    'Rio de Janeiro': {'coords': [-22.9068, -43.1729], 'geocode': 3304557},
    'Natal': {'coords': [-5.795, -35.2094], 'geocode': 2408102},
    'Porto Alegre': {'coords': [-30.0346, -51.2302], 'geocode': 4314902},
    'Porto Velho': {'coords': [-8.76077, -63.9039], 'geocode': 1100205},
    'Boa Vista': {'coords': [2.81999, -60.672], 'geocode': 1400100},
    'Florianópolis': {'coords': [-27.5954, -48.5477], 'geocode': 4205407},
    'São Paulo': {'coords': [-23.5505, -46.6333], 'geocode': 3550308},
    'Aracaju': {'coords': [-10.9472, -37.0731], 'geocode': 2800308},
    'Palmas': {'coords': [-10.1675, -48.3558], 'geocode': 1721000}
}

# Parâmetros comuns para todas as requisições
params_template = {
    'disease': 'dengue',
    'format': 'json',
    'ew_start': 1,
    'ew_end': 50,  # Ajustar conforme necessário
    'ey_start': 2024,
    'ey_end': 2024
}

# Função para obter dados de dengue para uma cidade específica
def get_dengue_data(geocode):
    params = params_template.copy()
    params['geocode'] = geocode
    response = requests.get('https://info.dengue.mat.br/api/alertcity', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/mapadengue')
def mapadengue():
    # Dicionário para armazenar o número de casos por capital
    casos_por_capital = {}

    # Obter dados para cada capital
    for capital, info in capitais.items():
        data = get_dengue_data(info['geocode'])
        if data:
            # Somar todos os casos nas semanas retornadas
            casos = sum(item.get('casos', 0) for item in data)
            casos_por_capital[capital] = casos
        else:
            casos_por_capital[capital] = 0

    # Criar mapa
    mapa = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

    # Adicionar marcadores para cada capital
    for cidade, info in capitais.items():
        coord = info['coords']
        casos = casos_por_capital.get(cidade, 0)
        folium.Marker(
            location=coord,
            popup=f'{cidade}: {casos} casos',
            icon=folium.Icon(color='red' if casos > 0 else 'green')
        ).add_to(mapa)

    # Renderizar o mapa para HTML
    mapa_html = mapa._repr_html_()

    return render_template('mapadengue.html', mapa=Markup(mapa_html))



#IDENTIFICAÇÃO DAS PÁGINAS HTML

@app.route('/resultado-pesquisa-impactos')
def resultadopesquisa():
    page = 1  # Defina o valor padrão para 'page' aqui
    total_pages = 1  # Defina o valor padrão para 'total_pages' aqui
    return render_template('resultado-pesquisa-impactos.html', page=page, total_pages=total_pages)

@app.route('/pesquisar', methods=['GET', 'POST'])
def pesquisar():
    if request.method == 'POST':
        # Se o formulário foi enviado, obtenha a consulta do formulário POST
        query = request.form.get('query', '')
    else:
        # Se a solicitação é GET, obtenha a consulta dos parâmetros da URL
        query = request.args.get('query', '')

    keywords = ["Mudanças Climáticas", "Efeito Estufa", "Aquecimento Global", "Impacto Ambiental"]
    page = int(request.args.get('page', 1))  # Obtenha o número da página da URL
    results_per_page = 10  # Número de resultados por página
    start = (page - 1) * results_per_page + 1
    apiKey = 'AIzaSyC_fMenI7tZa1gp478-ymQL7PTKygyQ4fk'
    customSearchId = 'b5e1d48951aa44edf'

    query += ' ' + ' '.join(keywords)

    params = {
        'q': query,
        'lr': 'lang_pt',  # Filtrar os resultados para português
        'hl': 'pt-BR',  # Configurar o idioma da pesquisa como português do Brasil
        'gl': 'br',
        'cx': 'b5e1d48951aa44edf',
        'key': 'AIzaSyC_fMenI7tZa1gp478-ymQL7PTKygyQ4fk',
        'start': start
    }

    try:
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
        data = response.json()
        search_results = data.get('items', [])

        total_results = data.get('searchInformation', {}).get('totalResults', 0)

        total_pages = (int(total_results) - 1) // results_per_page + 1


        # Ajuste para usar a primeira palavra do parágrafo como título, se não houver título
        for result in search_results:
            if 'title' not in result and 'snippet' in result:
                snippet = result['snippet']
                soup = BeautifulSoup(snippet, 'html.parser')
                first_word = soup.get_text().split()[0]
                result['title'] = first_word

        # Filtrar resultados com títulos que não contenham a palavra "Untitled"
        filtered_results = [result for result in search_results if is_valid_result(result)]

        return render_template('resultado-pesquisa-impactos.html', results=filtered_results, page=page, total_pages=total_pages)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)
    

@app.route ('/clima_tempo')
def clima_tempo():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('clima_tempo.html', username=session['username'])
    else:
        return redirect('/login')


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route ('/dengueinsight')
def dengueinsight():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('dengueinsight.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/pagina_principal/<string:fragment>')
def pagina_principal_fragment(fragment=None):
    # Se o fragmento estiver presente, você pode usá-lo no seu código Python
    # por exemplo, para determinar qual âncora deve ser ativada.
    return render_template('pagina_principal.html', fragment=fragment)

@app.route ('/sobre_nos')
def sobre_nos():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('sobre_nos.html', username=session['username'])
    else:
        return redirect('/login')



@app.route ('/maps_calor')
def maps_calor():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('maps_calor.html', username=session['username'])
    else:
        return redirect('/login')

@app.route ('/manual')
def manual():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('manual.html', username=session['username'])
    else:
        return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in'] and session['role'] == 'user':
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/login')



@app.route('/gerenciar_conta', methods=['GET', 'POST'])
def gerenciar_conta():
    if 'logged_in' in session and session['logged_in']:
        user_name = session.get('username')  # Obtém o nome do usuário da sessão

        if request.method == "POST":
            # Verifica se o usuário está logado e se é uma solicitação POST
            email = session.get('usu_email')  # Obtém o e-mail do usuário da sessão
            if not email:  # Se o e-mail não estiver presente na sessão
                flash("Usuário não encontrado.", "error")  # Exibe uma mensagem de erro
                return redirect(url_for('manual'))  # Redireciona o usuário para a página de login

            # Restante do código para atualizar a senha
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            # Verifica se a nova senha e a confirmação são iguais
            if new_password != confirm_password:
                flash("Nova senha e confirmação de senha não coincidem.", "error")
                return render_template('gerenciar_conta.html', user_name=user_name)

            usuario = Usuario()
            # Verifica se o e-mail fornecido corresponde ao e-mail do usuário atualmente logado na sessão
            if usuario.check_email(email):
                # Se o e-mail atual corresponde, verifica se a senha atual está correta
                if usuario.check_password(email, current_password):
                    # Se a senha atual está correta, atualiza a senha
                    if usuario.update_password(email, new_password):
                        flash("Senha alterada com sucesso!", "success")  # Mensagem de sucesso             
                    else:
                        flash("Não foi possível atualizar a senha.", "error")
                        return render_template('gerenciar_conta.html', user_name=user_name)
                else:
                    flash("Senha atual incorreta.", "error")
                    return render_template('gerenciar_conta.html', user_name=user_name)
            else:
                flash("E-mail atual incorreto.", "error")
                return render_template('gerenciar_conta.html', user_name=user_name)

        return render_template('gerenciar_conta.html', user_name=user_name)

    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)  