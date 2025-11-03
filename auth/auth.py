import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from models import Usuario

SECRET_KEY = "SUA_CHAVE_SECRETA_AQUI"

#1.PROTETOR DE ROTAS

def token_required(admin_only=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"ERRO": "TOKEN NÃO FORNECIDO!"}), 401
            try:
                token = token.replace("Bearer ", "")
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                usuario = Usuario.query.get(data['id'])
                if not usuario:
                    return jsonify({"ERRO": "USUÁRIO NÃO ENCONTRADO!"}), 401
                if admin_only and not usuario.admin:
                    return jsonify({"ERRO": "PERMISSÃO NEGADA!"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"ERRO": "TOKEN EXPIRADO!"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"ERRO": "TOKEN INVÁLIDO!"}), 401
            return f(usuario, *args, **kwargs)
        return wrapper
    return decorator 

#2.GERAR TOKEN:

def gerar_token(usuario):
    payload = {
        "id": usuario.id,
        "admin": usuario.admin,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
        