from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Usuario
from auth.auth import token_required, gerar_token

app_routes = Blueprint("usuarios_routes", __name__)

#1.REGISTRO DE USUÁRIOS:

@app_routes.route('/registro_usuarios', methods=['POST'])
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

#2.LOGIN 

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

#3.ATUALIZAR USUÁRIO:

@app_routes.route('/atualizar_usuario/<int:id>', methods=['POST'])
def atualizar_usuario(usuario_logado, id):
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"ERRO": "USUÁRIO NÃO ENCONTRADO!"}), 404
    
    if usuario_logado.id != usuario.id and not usuario_logado.admin:
        return jsonify({"ERRO": "VOCÊ NÃO TEM PERMISSÃO PARA ALTERAR ESTE USUÁRIO!"}), 403
    
    dados = request.get_json()
    nome = dados.get("nome")
    email = email.get("email")
    senha = senha.get("senha")

    if nome:
        usuario.nome = nome
    if email:
            usuario_existente = usuario.query.filter(Usuario.email == email, Usuario.id !=id).firts()
            if usuario_existente:
                return jsonify({"ERRO": "E-MAIL JÁ ESTÁ EM USO!"}), 400
            usuario.email = email

    if senha:
        usuario.senha = generate_password_hash(senha)
    
    db.session.commit()
    return jsonify({"mensagem": "USUÁRIO ATUALIZADO COM SUCESSO!"}), 200

#4.CADASTRAR ADMIN:
@app_routes.route('/cadastro_admin', methods=['POST'])
@token_required(admin_only=True)
def cadastro_admin():
    dados = request.get_json()

    if not dados:
        return jsonify({"ERRO": "NENHUM DADOS ENVIADO!"}), 400
    
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    if not nome or not email or not senha:
        return jsonify({"ERRO": "TODOS OS CAMPOS SAÕ OBRIGÁTORIOS!"}), 400
    
    usuario_existente =  Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"ERRO": "E-MAIL JÁ CADASTRADO!"}), 400
    
    novo_admin = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        admin=True
    )

    db.session.add(novo_admin)
    db.session.commit()

    return jsonify({"mensagem": f"ADMINISTRADOR {nome} CRIADO COM SUCESSO!"}), 201

#5.REMOVER USUÁRIO

@app_routes.route('/remover_usuario/<int:id>', methods=['DELETE'])
@token_required(admin_only=True)
def remover_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"ERRO": "USUÁRIO NÃO ENCONTRADO!"}), 404
        
        db.session.delete(usuario)
        db.session.commit()

        return jsonify({"mensagem": "USUÁRIO REMOVIDO COM SUCESSO!"}), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500