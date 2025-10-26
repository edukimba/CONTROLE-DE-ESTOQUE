from flask import Blueprint, request, jsonify
from database import db
from models import Movimentacoes, Produtos

app_routes = Blueprint('app_routes', __name__)

#CRIAR NOVA MOVIMENTAÇÃO:

@app_routes.route('/nova_movimentacao', methods=['POST'])
def nova_movimentacao():
    dados = request.get_json()
    try:
        tipo = dados.get('tipo')
        quantidade = float(dados.get('quantidade'))
        produto_id = dados.get('produto_id')

        produto = Produtos.query.get(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado!"}), 404
        
#ATUALIZAR O ESTOQUE:

        if tipo == 'entrada':
            produto.quantidade += quantidade
        elif tipo == 'saida':
            if produto.quantidade < quantidade:
                return jsonify({"erro": "Estoque insulficiente para saída!"}), 400
            produto.quantidade -= quantidade
        else:
            return jsonify({"erro": "Tipo de movimentação inválida,use 'entrada' ou 'saida'."})
        
        nova_movimentacao = Movimentacoes(
            tipo=tipo,
            quantidae=quantidade,
            produto_id=produto_id
        )

        db.session.add(nova_movimentacao)
        db.session.commit()

        return jsonify({
            "mensagem": "Movimentação registrada com sucesso!",
            "produto":{
                "nome": produto.nome,
                "quantidade_atual": produto.quantidade
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Ocorreu um erro interno: {str(e)}"}), 500


#LISTAR ENTRADAS E SAÍDAS DE PRODUTOS:

@app_routes.route('/movimentacoes', methods=['GET'])
def controle_de_produtos():
    tipo = request.args.get('tipo') 

    if tipo in ["entrada", "saida"]:
        produtos_filtrados = Produtos.query.all()

    resultado = [
        {"id": t.id, "tipo": t.tipo, "nome": t.nome, "preco": t.preco, "quantidade": t.quantidade, "descricao": t.descricao}
        for t in produtos_filtrados
    ]

    return jsonify(resultado), 200