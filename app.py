from flask import Flask
from database import db
from routes.routes_produtos import app_routes as produtos_routes
from routes.routes_movimentacoes import app_routes as movimentacoes_routes
from routes_auth import auth_routes
from routes.routes_usuarios import app_routes as usuarios_routes

app = Flask(__name__)

#CONFIGURAR BANCO DE DADOS:p

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#INICIAR O BANCO DE DADOS:

db.init_app(app)

#REGISTRAR BLUEPRINTS:

app.register_blueprint(produtos_routes, url_prefix='/produtos')
app.register_blueprint(movimentacoes_routes, url_prefix='/movimentacoes')
app.register_blueprint(usuarios_routes)
app.register_blueprint(auth_routes, url_prefix='/auth')

@app.route('/')
def index():
    return "API DE ESTOQUE ONLINE!"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)