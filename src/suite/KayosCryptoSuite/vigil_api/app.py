import os
from flask import Flask
from flask_cors import CORS
from vigil_api.routes import routes
from vigil_api.license_routes import license_routes
from vigil_api.quantum_routes import quantum_routes

app = Flask(__name__)
CORS(app)

# Registra todos os blueprints
app.register_blueprint(routes)
app.register_blueprint(license_routes)
app.register_blueprint(quantum_routes)

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv('FLASK_HOST', '127.0.0.1'), port=5000)
