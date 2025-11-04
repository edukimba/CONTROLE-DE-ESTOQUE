from flask import Blueprint, jsonify
import logging

#TRATAMENTO DE ERROS:

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'erro': 'ROTA NÃO ENCONTRADA!'}), 404

@errors.app_errorhandler(400)
def bed_request_error(error):
    return jsonify({'erro': 'REQUISIÇÃO INVÁLIDA!'}), 400

@errors.app_errorhandler(500)
def internal_error(error):
    logging.exception("ERRO INTERNO:")
    return jsonify({'erro': 'ERRO INTERNO DO SERVIDOR!'}), 500

@errors.app_errorhandler(Exception)
def unhandler_exception(error):
    return jsonify({"erro": str(error)}), 500