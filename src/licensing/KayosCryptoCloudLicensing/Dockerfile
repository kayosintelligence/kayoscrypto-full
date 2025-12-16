# Etapa 1: Base da imagem
FROM python:3.10-slim

# Etapa 2: Define diretório de trabalho
WORKDIR /app

# Etapa 3: Copia arquivos do projeto
COPY . /app

# Etapa 4: Instala as dependências
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Etapa 5: Expõe a porta do Flask
EXPOSE 5000

# Etapa 6: Comando para iniciar o app
CMD ["python", "-m", "k_vigil_api.app"]
