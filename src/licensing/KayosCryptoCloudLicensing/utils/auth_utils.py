import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify
import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis-kayos"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'mensagem': 'Token ausente!'}), 401

        try:
            if redis_client.get(token):
                return jsonify({'mensagem': 'Token já utilizado ou expirado'}), 401

            dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            exp_timestamp = dados['exp']
            ttl = exp_timestamp - datetime.datetime.now(datetime.timezone.utc).timestamp()
            redis_client.setex(token, int(ttl), "usado")

        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido'}), 401

        return f(*args, **kwargs)

    return decorated
