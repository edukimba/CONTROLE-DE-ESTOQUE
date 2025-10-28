from flask import Blueprint, request, jsonify
from database import db
from models import Produtos
from sqlalchemy import and_

app_routes = Blueprint('app_routes', __name__)

#1.CADASTRAR NOVO PRODUTO:

@app_routes.route('/cadastrar_produto', methods=['POST'])
def novo_produto():
    dados = request.get_json()
    try:
        if not dados:
            return jsonify({"ERRO": "NENHUM DADO ENVIADO,ENVIE UM JSON VÁLIDO!"}), 400
        
        campos_obrigatorios = ['tipo', 'nome', 'descricao', 'quantidade', 'preco']
        if not all(campo in dados for campo in campos_obrigatorios):
            return jsonify({"ERRO": "TODOS OS CAMPOS SÃO OBRIGATÓRIOS!"}), 400
        
        try:
            quantidade = float(dados['quantidade'])
            preco = float(dados['preco'])
        except ValueError:
            return jsonify({"ERRO": "O CAMPO 'quantidade' E 'preco' DEVEM SER NUMÉRICOS!"}), 400
        
        novo = Produtos(
            tipo=dados['tipo'],
            nome=dados['nome'],
            descricao=dados.get('descricao', ''),
            preco=preco,
            quantidade=quantidade,
            )
            
        
        db.session.add(novo)
        db.session.commit()

        return jsonify({"mensagem": "PRODUTO ADICIONADO AO ESTOQUE!"}), 201

    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#2.LISTAR TODOS OS PRODUTOS:

@app_routes.route('/listar_produtos', methods=['GET'])
def listar_produtos():
    try:
        produtos = Produtos.query.all()
        resultado = []
        for t in produtos:
            resultado.append({
                "tipo": t.tipo,
                "id": t.id,
                "descricao": t.descricao,
                "preco": t.preco,
                "quantidade": t.quantidade
            })

        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO!{str(e)}"}), 500

#3.BUSCAR PRODUTO POR NOME:

@app_routes.route('/buscar_por_nome', methods=['GET'])
def buscar_produto():
    try:
        termo = request.args.get('nome', '').strip()
        if not termo:
            return jsonify({"ERRO": "ENVIE UM 'nome' PARA REALIZAR A BUSCA!"}), 400
        
        palavras = termo.split()
        filtros = [produtos.nome.ilike(f"%{p}") for p in palavras]
        produtos = Produtos.query.filter(and_(*filtros)).all()

        if not produtos:
            return jsonify({"ERRO": "NENHUM PRODUTO ENCONTRADO!"}), 404
        
        resultado = []
        for p in produtos:
            resultado.append({
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "quantidade": p.quantidade,
                "preco": p.preco
            })

            return jsonify({"resultados": resultado}), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO!: {str(e)}"}), 500

#4.LISTAR PRODUTOS COM BAIXO ESTOQUE:

@app_routes.route('/baixo_estoque', methods=['GET'])
def listar_baixo_estoque():
    try:
        limite = request.args.get('limite', default=5, type=int)
        produtos = Produtos.query.filter(Produtos.quantidade <= limite).all()

        if not produtos:
            return jsonify({"ERRO": "NENHUM PRODUTO COM ESTOQUE MENOR OU IGUAL A {limite} ENCONTRADO!"}), 200
        
        resultado = []
        for p in produtos:
            resultado.append({
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "quantidade": p.quantidade,
                "preco": p.preco
            })

        return jsonify({
            "mensagem": f"PRODUTOS COM ESTOQUE MENOR OU IGUAL A {limite}:",
            "produtos": resultado
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500

#5.VER UM PRODUTO ESPECÍFICO:

@app_routes.route('/buscar_por_id<int:id>', methods=['GET'])
def buscar_produto_especifico(id):
    try:
        produto = Produtos.query.get(id)

        if not produto:
            return jsonify({"ERRO": "PRODUTO NÃO ENCONTRADO!"}), 404
        
        return jsonify({
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "quantidade": produto.quantidade,
            "preco": produto.preco
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500

#ATUALIZAR PRODUTO:

@app_routes.route('/atualizar_produto/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    produtos = Produtos.query.get(id)
    if not produtos:
        return jsonify({"ERRO": "PRODUTO NÃO ENCONTRADO!"}), 404
    
    dados = request.get_json()

    produtos.nome = dados.get('nome', produtos.nome)
    produtos.descricao = dados.get('descricao', produtos.descricao)
    produtos.preco = dados.get('preco', produtos.preco)
    produtos.quantidade = dados.get('quantidade', produtos.quantidade)

    db.session.commit()

    return jsonify({"mensagem": "PRODUTO ATUALIZADO COM SUCESSO!"}), 201

#REMOVER PRODUTO:

@app_routes.route('remover_produto/<int:id>', methods=['DELETE'])
def remover_produto(id):
    try:
        produtos = Produtos.query.get(id)
        if not produtos:
            return jsonify({"ERRO": "PRODUTO NÃO ENCONTRADO!"}), 404
        
        db.session.delete(produtos)
        db.session.commit()

        return jsonify({"mensagem": "PRODUTO REMOVIDO COM SUCESSO!"}), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    