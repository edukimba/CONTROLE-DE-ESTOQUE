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
def nova_movimentacao(usuario):
    dados = request.get_json()
    
    try:
        tipo = dados.get('tipo')
        quantidade = float(dados.get('quantidade', 0))
        produto_id = dados.get('produto_id')

        
        if not tipo or not quantidade or not produto_id:
            return jsonify({"erro": "Campos 'tipo', 'quantidade' e 'produto_id' são obrigatórios!"}), 400

        produto = Produtos.query.get(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado!"}), 404
        
        
        if tipo == 'entrada':
            produto.quantidade += quantidade
        elif tipo == 'saida':
            if produto.quantidade < quantidade:
                return jsonify({"erro": "Estoque insuficiente para saída!"}), 400
            produto.quantidade -= quantidade
        else:
            return jsonify({"erro": "Tipo de movimentação inválido. Use 'entrada' ou 'saida'."}), 400
        
        
        nova_movimentacao = Movimentacoes(
            tipo=tipo,
            quantidade=quantidade,
            produto_id=produto_id
        )

        db.session.add(nova_movimentacao)
        db.session.commit()

        return jsonify({
            "mensagem": "Movimentação registrada com sucesso!",
            "produto": {
                "nome": produto.nome,
                "quantidade_atual": produto.quantidade
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Ocorreu um erro interno: {str(e)}"}), 500

#2.LISTAR TODAS MOVIMENTAÇÕES:

@app_routes.route('/todas_movimentacoes', methods=['GET'])
@token_required(admin_only=True)
def todas_movimentacoes(usuario):
    try:
        movimentacoes = Movimentacoes.query.all()

        if not movimentacoes:
            return jsonify({"mensagem": "Nenhuma movimentação registrada ainda."}), 200

        resultado = []
        for m in movimentacoes:
            produto = Produtos.query.get(m.produto_id)  

            resultado.append({
                "id_movimentacao": m.id,
                "tipo": m.tipo,
                "quantidade": m.quantidade,
                "data": m.data.strftime("%d/%m/%Y %H:%M:%S") if hasattr(m, 'data') and m.data else None,
                "produto": {
                    "id": produto.id if produto else None,
                    "nome": produto.nome if produto else "Produto excluído",
                    "descricao": produto.descricao if produto else None,
                    "preco": produto.preco if produto else None
                }
            })

        return jsonify({"movimentacoes": resultado}), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"Ocorreu um erro interno: {str(e)}"}), 500
       
#3.VER MOVIMENTAÇÃO ESPECÍFICA:

@app_routes.route('/buscar_mov_id/<int:id>', methods=['GET'])
@token_required(admin_only=True)
def buscar_movimentacao_especifica(usuario, id):
    try:
        movimentacao = Movimentacoes.query.get(id)

        if not movimentacao:
            return jsonify({"ERRO": "MOVIMENTAÇÃO NÃO ENCONTRADA!"}), 404

        produto = Produtos.query.get(movimentacao.produto_id)

        return jsonify({
            "id_movimentacao": movimentacao.id,
            "tipo": movimentacao.tipo,
            "quantidade": movimentacao.quantidade,
            "data": movimentacao.data.strftime("%d/%m/%Y %H:%M:%S") if hasattr(movimentacao, 'data') and movimentacao.data else None,
            "produto": {
                "id": produto.id if produto else None,
                "nome": produto.nome if produto else "Produto excluído",
                "descricao": produto.descricao if produto else None,
                "preco": produto.preco if produto else None,
                "quantidade_atual": produto.quantidade if produto else None
            }
        }), 200

    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500

#4.REMOVER MOVIMENTAÇÃO:

@app_routes.route('/remover_movimentacao/<int:id>', methods=['DELETE'])
@token_required(admin_only=True)
def remover_movimentacao(usuario, id):
    try:
        movimentacao = Movimentacoes.query.get(id)
        if not movimentacao:
            return jsonify({"ERRO": "MOVIMENTAÇÃO NÃO ENCONTRADA!"}), 404
        
        db.session.delete(movimentacao)
        db.session.commit()

        return jsonify({"mensagem": "MOVIMENTAÇÃO REMOVIDA COM SUCESSO!"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#5.MOVIMENTAÇÕES POR UMA DETERMINADA DATA:

@app_routes.route('/mov_por_data', methods=['GET'])
@token_required(admin_only=True)
def movi_por_data(usuario):
    try:
        data_str = request.args.get('data')

        if not data_str:
            return jsonify({"ERRO": "ENVIE O PARÂMETRO 'data' NO FORMATO YYYY-MM-DD!"}), 400
        
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"ERRO": "FORMATO DE DATA INVÁLIDO! USE YYYY-MM-DD."}), 400
        
        movimentacoes = Movimentacoes.query.filter(
            db.func.date(Movimentacoes.data) == data
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
                "data": m.data.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "mensagem": f"MOVIMENTAÇÕES DO DIA {data_str}:",
            "movimentacoes": resultado            
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#6.PRODUTOS COM MAIS MOVIMENTAÇÕES:

@app_routes.route('/relatorio_mais_movimentacoes', methods=['GET'])
@token_required(admin_only=True)
def relatorio_mais_mov(usuario):
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

