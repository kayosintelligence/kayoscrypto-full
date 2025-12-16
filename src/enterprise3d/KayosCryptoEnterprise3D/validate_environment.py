#!/usr/bin/env python3
"""
 VALIDAÇÃO DO AMBIENTE ATUAL
"""

import sys
import subprocess

def check_python_version():
 """Verificar versão do Python"""
 version = sys.version_info
 print(f" Python {version.major}.{version.minor}.{version.micro}")
 return version.major == 3 and version.minor >= 8

def check_environment():
 """Verificar ambiente virtual"""
 import os
 if 'VIRTUAL_ENV' in os.environ:
 print(f" Ambiente virtual: {os.environ['VIRTUAL_ENV']}")
 return True
 else:
 print(" Não está em ambiente virtual")
 return False

def check_dependencies():
 """Verificar dependências atuais"""
 dependencies = [
 'psycopg2',
 'fastapi', 
 'uvicorn',
 'cryptography',
 'pydantic'
 ]
 
 missing = []
 for dep in dependencies:
 try:
 __import__(dep)
 print(f" {dep}")
 except ImportError:
 missing.append(dep)
 print(f" {dep}")
 
 return len(missing) == 0

def main():
 print(" VALIDAÇÃO DO AMBIENTE KAYOSCRYPTO")
 print("=" * 40)
 
 results = []
 
 print("\n1. Versão Python:")
 results.append(check_python_version())
 
 print("\n2. Ambiente Virtual:")
 results.append(check_environment())
 
 print("\n3. Dependências:")
 results.append(check_dependencies())
 
 print("\n" + "=" * 40)
 if all(results):
 print(" AMBIENTE VALIDADO - PRONTO PARA OQS")
 return True
 else:
 print(" CORRIJA O AMBIENTE ANTES DE CONTINUAR")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
