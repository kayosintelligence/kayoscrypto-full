from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from crypto_engine import crypto_engine

class CryptoAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/encrypt':
            self.handle_encrypt()
        elif self.path == '/decrypt':
            self.handle_decrypt()
        else:
            self.send_error(404)
    
    def handle_encrypt(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Processar com engine real
        result = crypto_engine.symbiotic_aes(
            data['text'], 
            data.get('key', 'default_symbiotic_key')
        )
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'encrypted': result,
            'algorithm': 'symbiotic_aes_v1'
        }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8888), CryptoAPIHandler)
    print(" KayosCrypto API running on port 8888")
    server.serve_forever()
