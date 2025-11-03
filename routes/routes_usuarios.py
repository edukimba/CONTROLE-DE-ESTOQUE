from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Usuario
from auth.auth import token_required, gerar_token

app_routes = Blueprint("usuarios_routes", __name__)

#1.REGISTRO DE USUÁRIOS:

@app_routes.route('/registro', methods=['POST'])
def registro():
    dados = request.get_json()

    if not dados:
        return jsonify({"ERRO": "NENHUM DADO ENVIADO!"}), 400
    
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    if not nome or not email or not senha:
        return jsonify({"ERRO": "TODOS OS CAMPOS SÃO OBRIGÁTORIOS!"}), 400
    
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"ERRO": "E-MAIL JÁ JÁ CADASTRADO!"}), 400
    
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        admin=False
    )
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"mensagem": "USUÁRIO REGISTRADO COM SUCESSO!"}), 201

#LOGIN 

@app_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"ERRO": "USUÁRIO E SENHA INVÁLIDOS!"}), 401
    
    token = gerar_token(usuario)
    return jsonify({"token": token, "admin": usuario.admin})
