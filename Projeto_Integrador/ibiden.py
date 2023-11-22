from flask import Flask, request, render_template, redirect, url_for
import requests
import logging

from bs4 import BeautifulSoup
app = Flask(__name__, static_url_path='/static')

#CLIMA&TEMPO

# Substitua 'YOUR_API_KEY' pela sua chave de API WeatherAPI.com
api_key = 'ea86ffcaee9a4737972222744230410'

# URL base da API
base_url = 'http://api.weatherapi.com/v1/current.json'

@app.route('/')
def index():
    return render_template('index.html', umidade='', temperatura='', uv='', velocidade_vento='', cobertura_nuvens='', precipitacao='', pressao= '',sensacao = '', visibilidade='', condicao='')


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
            umidade = int(data['current']['humidity'])
            temperatura = int(data['current']['temp_c'])
            uv = int(data['current']['uv'])
            velocidade_vento = int(data['current']['wind_kph'])
            cobertura_nuvens = int(data['current']['cloud'])
            umidade = int(data['current']['humidity'])
            precipitacao = data['current']['precip_mm']
            pressao = int(data['current']['pressure_mb'])
            sensacao = int(data['current']['feelslike_c'])
            visibilidade = int(data['current']['vis_km'])
            condicao = data['current']['condition']

            return render_template('clima_tempo.html', umidade=umidade, temperatura=temperatura, uv=uv, velocidade_vento=velocidade_vento,cobertura_nuvens=cobertura_nuvens, precipitacao=precipitacao, pressao=pressao,sensacao
                           =sensacao, visibilidade=visibilidade, condicao=condicao)
        else:
            return render_template('clima_tempo.html'), f"Nome inválido de pesquisa!"
    except Exception as e:
        return f"Nome inválido de pesquisa!"
    

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

def is_valid_result(result):
        # Função auxiliar para verificar se um resultado é válido
        if 'title' in result:
            title = result['title'].strip().lower()
            return 'untitled' not in title
        return False


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
    return render_template('clima_tempo.html')

@app.route ('/geolocalizacao')
def geolocalizacao():
    return render_template('geolocalizacao.html')

@app.route('/pagina_principal/<string:fragment>')
def pagina_principal_fragment(fragment=None):
    # Se o fragmento estiver presente, você pode usá-lo no seu código Python
    # por exemplo, para determinar qual âncora deve ser ativada.
    return render_template('pagina_principal.html', fragment=fragment)

@app.route ('/sobre_nos')
def sobre_nos():
    return render_template('sobre_nos.html')

@app.route ('/maps')
def maps():
    return render_template('maps.html')

@app.route ('/maps_calor')
def maps_calor():
    return render_template('maps_calor.html')

@app.route ('/manual')
def manual():
    return render_template('manual.html')

if __name__ == '__main__':
    app.run(debug=True)   