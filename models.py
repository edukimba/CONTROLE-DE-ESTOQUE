from database import db
from datetime import datetime

#PRODUTOS:

class produtos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    preco = db.Column(db.Float, nullable=True)

#MOVIMENTAÇÕES:

class movimentacoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeingnKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Colum(db.Datetime, default =datetime.utcnow)

    produto = db.relationship('produto', backref=db.backref('movimentacoes', lazy=True))