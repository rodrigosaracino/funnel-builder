# Use Python 3.12 como base
FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para bcrypt
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do projeto
COPY . .

# Cria diretório para o banco de dados
RUN mkdir -p /app/data

# Expõe a porta 8000
EXPOSE 8000

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação
CMD ["python", "funnel_builder.py"]
