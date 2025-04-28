import os
import pyodbc
import pandas as pd
from flask import Flask, jsonify, request
from decouple import Config, RepositoryEnv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)

# Carregar as variáveis do arquivo .env na pasta instance
config = Config(RepositoryEnv('instance/config.env'))

# Configuração do JWT
TOKEN = config('TOKEN')
app.config["JWT_SECRET_KEY"] = TOKEN # Substitua por uma chave segura armazenada no ambiente
jwt = JWTManager(app)

# Configuração da string de conexão com o SQL Server
DB_USER = config('DB_USER')
DB_PASS = config('DB_PASS')
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
DB_DRIVER = config('DB_DRIVER')

CONNECTION_STRING = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_HOST};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};Encrypt=Yes;TrustServerCertificate=Yes"

# Função para autenticação e geração de token (válido por 12 horas)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Verificar credenciais (substitua pela lógica real de autenticação)
    if username == "admin" and password == "admin123":  # Exemplo básico
        # Gerar token com validade de 12 horas
        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=12))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Credenciais inválidas"}), 401

# Função genérica para executar uma consulta SQL
def execute_query(sql_file):
    try:
        # Ler a consulta SQL da pasta 'queries'
        query = read_query_from_file(sql_file)
        if not query:
            return jsonify({"error": f"Arquivo {sql_file} não encontrado."}), 404

        # Usando pandas para executar a consulta e capturar colunas automaticamente
        connection = pyodbc.connect(CONNECTION_STRING)
        df = pd.read_sql(query, connection)

        # Convertendo o DataFrame para JSON
        resultado_json = df.to_dict(orient="records")

        # Fechar a conexão
        connection.close()

        return jsonify(resultado_json)

    except Exception as e:
        # Tratamento de erros
        return jsonify({"error": str(e)}), 500

# Função para ler a query do arquivo na pasta 'queries'
def read_query_from_file(filename):
    query_path = os.path.join('queries', filename)
    try:
        with open(query_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

# Rotas protegidas por autenticação
@app.route('/rankingHoje', methods=['GET'])
@jwt_required()
def get_rankingHoje():
    return execute_query('rankingHoje.sql')

@app.route('/estoquista', methods=['GET'])
@jwt_required()
def get_novaConsulta():
    return execute_query('estoquistas.sql')

# Executar o aplicativo
if __name__ == '__main__':
    app.run(debug=True)