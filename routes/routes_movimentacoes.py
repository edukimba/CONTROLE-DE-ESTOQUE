from flask import Blueprint, request, jsonify
from database import db
from models import Movimentacoes, Produtos
from datetime import datetime
from sqlalchemy import func
from auth.auth import token_required

app_routes = Blueprint('movimentacoes', __name__)

#1.CRIAR NOVA MOVIMENTAÇÃO:

@app_routes.route('/nova_movimentacao', methods=['POST'])
@token_required(admin_only=True)
def nova_movimentacao():
    dados = request.get_json()
    try:
        tipo = dados.get('tipo')
        quantidade = float(dados.get('quantidade'))
        produto_id = dados.get('produto_id')

        produto = Produtos.query.get(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado!"}), 404
        
#2.ATUALIZAR ESTOQUE:

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
    
#3.LISTAR TODAS MOVIMENTAÇÕES:

@app_routes.route('/todas_movimentacoes', methods=['GET'])
@token_required(admin_only=True)
def todas_movimentacoes():
    try:
        movimentacao = Movimentacoes.query.all()
        resultado = []
        for t in movimentacao:
            resultado.append({
                "id": t.id,
                "nome": t.nome,
                "descricao": t.descricao,
                "quantidade": t.quantidade,
                "preco": t.preco
            })

        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#4.LISTAR ENTRADAS E SAÍDAS DE PRODUTOS:

@app_routes.route('/controle_produtos', methods=['GET'])
@token_required(admin_only=True)
def controle_de_produtos():
    try:
        tipo = request.args.get('tipo') 
        if tipo in ["entrada", "saida"]:

            produtos_filtrados = Produtos.query.all()
            
            resultado = [
                {"id": t.id, "tipo": t.tipo, "nome": t.nome, "preco": t.preco, "quantidade": t.quantidade, "descricao": t.descricao}
                for t in produtos_filtrados
                ]
            return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO{str(e)}"}), 500
    
#5.VER MOVIMENTAÇÃO ESPECÍFICA:

@app_routes.route('/buscar_mov_id<int:id>', methods=['GET'])
@token_required(admin_only=True)
def buscar_movimentacao_especifica(id):
    try:
        movimentacao = Movimentacoes.query.get(id)

        if not movimentacao:
            return jsonify({"ERRO": "MOVIMENTAÇÃO NÃO ENCONTRADA!"}), 404
        
        return jsonify({
            "id": movimentacao.id,
            "nome": movimentacao.nome,
            "descricao": movimentacao.descricao,
            "quantidade": movimentacao.quantidade,
            "preco": movimentacao.preco
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500

#6.REMOVER MOVIMENTAÇÃO:

@app_routes.route('remover_movimentcao/<int:id>', methods=['DELETE'])
@token_required(admin_only=True)
def remover_movimentacao(id):
    try:
        movimentacoes = Movimentacoes.query.get(id)
        if not movimentacoes:
            return jsonify({"ERRO": "MOVIMENTAÇÃO NÃO ENCONTRADA!"}), 404
        
        db.session.delete(movimentacoes)
        db.session.commit()

        return jsonify({"mensagem": "MOVIMENTAÇÃO REMOVIDA COM SUCESSO!"}), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#7.MOVIMENTAÇÕES POR UMA DETERMINADA DATA:

@app_routes.route('/mov_por_data', methods=['GET'])
@token_required(admin_only=True)
def movi_por_data():
    try:
        data_str = request.args.get('data')

        if not data_str:
            return jsonify({"ERRO": "ENVIE O PARÂMETRO 'data' NO FORMATO YYYY-MM-DD!"}), 400
        
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"ERRO": "FORMATO DE DATA INVÁLIDO,USE O FORMATO YYYY-MM-DD!"}), 400
        
        movimentacoes = Movimentacoes.query.filter(
            db.func.date(movimentacoes.data) == data
        ).all()

        if not movimentacoes:
            return jsonify({"mensagem": f"NENHUMA MOVIMENTAÇÃO ENCONTRADA PARA {data_str}!"}), 200
        
        resultado = []
        for m in movimentacoes:
            resultado.append({
                "id": m.id,
                "produto_id": m.produto_id,
                "tipo": m.tipo,
                "quantidade": m.quantidade,
                "data": m.data.strtime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "mensagem": f"MOVIMENTAÇÕES DO DIA {data_str}:",
            "movimentacoes": resultado            
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#8.PRODUTOS COM MAIS MOVIMENTAÇÕES:

@app_routes.route('/mais_movimentacoes', methods = ['GET'])
@token_required(admin_only=True)
def relatorio_mais_mov():
    try:
        
        resultados = (
            db.session.query(
                Produtos.id,
                Produtos.nome,
                func.count(Movimentacoes.id).label('total_movimentacoes')
            )
            .join(Movimentacoes, Produtos.id == Movimentacoes.produto_id)
            .group_by(Produtos.id)
            .order_by(func.count(Movimentacoes.id).desc())
            .all()
        )

        if not resultados:
            return jsonify({"mensagem": "Nenhuma movimentação registrada."}), 404

        relatorio = []
        for r in resultados:
            relatorio.append({
                "id_produto": r.id,
                "nome": r.nome,
                "total_movimentacoes": r.total_movimentacoes
            })

        return jsonify({
            "total_produtos_com_movimentacoes": len(relatorio),
            "produtos": relatorio
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro interno: {str(e)}"}), 500

