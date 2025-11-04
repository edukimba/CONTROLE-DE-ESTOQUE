from flask import Blueprint, request, jsonify
from database import db
from models import Produtos
from sqlalchemy import and_
from auth.auth import token_required

app_routes = Blueprint('produtos', __name__)

#1.CADASTRAR NOVO PRODUTO:

@app_routes.route('/cadastrar_produto', methods=['POST'])
@token_required(admin_only=True)
def novo_produto(usuario):
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
        db.session.rollback()
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500
    
#2.LISTAR TODOS OS PRODUTOS:

@app_routes.route('/listar_produtos', methods=['GET'])
@token_required()
def listar_produtos(usuario):
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
@token_required()
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
        
        resultado = [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "quantidade": p.quantidade,
                "preco": p.preco
            }
            for p in produtos
        ]
        return jsonify({
            "resultados": resultado,
            "total": len(resultado)
            }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO!: {str(e)}"}), 500

#4.LISTAR PRODUTOS COM BAIXO ESTOQUE:

@app_routes.route('/baixo_estoque', methods=['GET'])
@token_required()
def listar_baixo_estoque(usuario):
    try:
        limite = request.args.get('limite', default=5, type=int)
        produtos = Produtos.query.filter(Produtos.quantidade <= limite).all()

        if not produtos:
            return jsonify({"ERRO": f"NENHUM PRODUTO COM ESTOQUE MENOR OU IGUAL A {limite} ENCONTRADO!"}), 200
        
        resultado = [
        
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "quantidade": p.quantidade,
                "preco": p.preco
            }
            for p in produtos
        ]
        return jsonify({
            "mensagem": f"PRODUTOS COM ESTOQUE MENOR OU IGUAL A {limite}:",
            "produtos": resultado,
            "total": len(resultado)
        }), 200
    
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500

#5.VER PRODUTO ESPECÍFICO:

@app_routes.route('/buscar_por_id/<int:id>', methods=['GET'])
@token_required()
def buscar_produto_especifico(usuario, id):
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

#6.ATUALIZAR PRODUTO:

@app_routes.route('/atualizar_produto/<int:id>', methods=['PUT'])
@token_required(admin_only=True)
def atualizar_produto(usuario, id):
    try:
        produto = Produtos.query.get(id)
        if not produto:
            return jsonify({"ERRO": "PRODUTO NÃO ENCONTRADO!"}), 404

        dados = request.get_json()
        if not dados:
            return jsonify({"ERRO": "NENHUM DADO ENVIADO!"}), 400

        produto.nome = dados.get('nome', produto.nome)
        produto.descricao = dados.get('descricao', produto.descricao)

        if 'preco' in dados:
            try:
                produto.preco = float(dados['preco'])
            except ValueError:
                return jsonify({"ERRO": "O CAMPO 'preco' DEVE SER UM NÚMERO!"}), 400

        if 'quantidade' in dados:
            try:
                produto.quantidade = float(dados['quantidade'])
            except ValueError:
                return jsonify({"ERRO": "O CAMPO 'quantidade' DEVE SER UM NÚMERO!"}), 400

        db.session.commit()

        return jsonify({
            "mensagem": "PRODUTO ATUALIZADO COM SUCESSO!",
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "descricao": produto.descricao,
                "quantidade": produto.quantidade,
                "preco": produto.preco
            }
        }), 200

    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500


#7.REMOVER PRODUTO:

@app_routes.route('/remover_produto/<int:id>', methods=['DELETE'])
@token_required(admin_only=True)
def remover_produto(usuario, id):
    try:
        produto = Produtos.query.get(id)
        if not produto:
            return jsonify({"ERRO": "PRODUTO NÃO ENCONTRADO!"}), 404

        db.session.delete(produto)
        db.session.commit()

        return jsonify({
            "mensagem": "PRODUTO REMOVIDO COM SUCESSO!",
            "produto_removido": {
                "id": produto.id,
                "nome": produto.nome,
                "descricao": produto.descricao,
                "preco": produto.preco
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO: {str(e)}"}), 500


#8.RELATORIO GERAL DO ESTOQUE:

@app_routes.route('/relatorio_geral', methods=['GET'])
@token_required(admin_only=True)
def relatorio_geral():
    try:
        baixo_estoque = request.args.get('baixo_estoque')

        LIMITE_ESTOQUE = 5

        if baixo_estoque and baixo_estoque.lower() == 'true':
            produtos = Produtos.query.filter(Produtos.quantidade <= LIMITE_ESTOQUE).all()
        else:
            produtos = Produtos.query.all()

        if not produtos:
            return jsonify({"ERRO": "NENHUM PRODUTO ENCONTRADO COM OS DADOS INFORMADOS!"}), 404
        
        relatorio = []
        valor_total_estoque = 0

        for p in produtos:
            valor_produto = p.quantidade * p.preco
            valor_total_estoque += valor_produto

            relatorio.append({
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "quantidade": p.quantidade,
                "preco_unitario": p.preco,
                "valor_total_produto": valor_produto
            })

        return jsonify({
            "total_produtos": len(produtos),
            "valor_total_estoque": valor_total_estoque,
            "produtos": relatorio
        }), 200
        
    except Exception as e:
        return jsonify({"ERRO": f"OCORREU UM ERRO INTERNO{str(e)}"}), 500