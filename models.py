from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash
#PRODUTOS:

class Produtos(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    preco = db.Column(db.Float, nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    produto = db.relationship('Produtos', backref='movimentacoes')

#MOVIMENTCOES:

class Movimentacoes(db.Model):
    __tablename__ = 'movimentacoes'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  
    quantidade = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    produto = db.relationship('Produtos', backref='movimentacoes')

#USUÁRIOS:

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        self.check_password_hash(self.senha_hash, senha)