# 📦 Controle de Estoque

Um sistema de controle de estoque desenvolvido com **Flask**, **SQLAlchemy**, **JWT**, e **PostgreSQL**, permitindo gerenciar usuários, produtos, categorias e histórico de movimentações.

---

## 🚀 Tecnologias Utilizadas

* **Python 3**
* **Flask**
* **Flask SQLAlchemy**
* **JWT Authentication**
* **PostgreSQL**
* **Postman** (testes manuais)

---

## 📁 Estrutura do Projeto

```
CONTROLE-DE-ESTOQUE/
│
├──api-flow/
│   └──CONTROLE-DE-ESTOQUE.pdf
├──auth/
│   └──__init__.py
│   └──auth.py
├──instace/
│   └──estoque.db
├──postman/
│   └──CONTROLE-DE-ESTOQUE API.postman_collection.json
├──routes/
│   └──routes_movimentacoes.py
│   └──routes_produtos.py
│   └──routes_usuarios.py
├── app.py
├── database.py
├── errors.py
├── models.py
├── utils/
│   └── auth.py
├── README.md
├── requirements.txt
└── ...
```
---

## 🔐 Autenticação

A aplicação utiliza **JWT**.

### Gerar token:

* Rota de login devolve `token` válido por 2 horas.




## 📌 Funcionalidades Principais

* Autenticação JWT
* Controle de permissões (admin e usuário comum)
* Cadastro e gerenciamento completo de produtos
* Categorias vinculadas aos produtos
* Registro de entradas e saídas do estoque
* Histórico detalhado de movimentações

---

## 📄 Licença

Este projeto é open-source e pode ser utilizado livremente.

---

## ✨ Autor

**Edu Santos** – Desenvolvimento completo da API.

---
