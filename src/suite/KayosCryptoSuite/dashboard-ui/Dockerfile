# dashboard-ui/Dockerfile

# Etapa 1: Usar Node 20 para compatibilidade com Vite
FROM node:20-alpine

# Diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Copia os arquivos de dependência
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante dos arquivos da aplicação
COPY . .

# Expõe a porta padrão do Vite
EXPOSE 5173

# Usa o servidor de desenvolvimento do Vite com acesso externo
CMD ["npm", "run", "dev", "--", "--host"]
