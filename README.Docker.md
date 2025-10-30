# 🐳 Funnel Builder - Guia Docker

Guia completo para executar o Funnel Builder usando Docker e Docker Compose.

---

## 📋 Pré-requisitos

- Docker instalado (versão 20.10 ou superior)
- Docker Compose instalado (versão 1.29 ou superior)

### Verificar instalação:
```bash
docker --version
docker-compose --version
```

---

## 🚀 Como Usar

### 1. Iniciar a aplicação

No diretório do projeto, execute:

```bash
docker-compose up -d
```

**Flags:**
- `-d`: Executa em background (detached mode)
- Omita `-d` para ver os logs em tempo real

### 2. Verificar status

```bash
docker-compose ps
```

Você deve ver o container `funnel-builder-app` com status `Up`.

### 3. Acessar a aplicação

Abra seu navegador em:
```
http://localhost:8000
```

### 4. Ver logs

```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Logs apenas do serviço funnel-builder
docker-compose logs -f funnel-builder
```

### 5. Parar a aplicação

```bash
# Parar (mantém volumes e dados)
docker-compose stop

# Parar e remover containers (mantém volumes)
docker-compose down

# Parar, remover containers E volumes (APAGA DADOS!)
docker-compose down -v
```

---

## 🔄 Rebuild (após mudanças no código)

Se você modificou o código e quer reconstruir a imagem:

```bash
# Rebuild e reiniciar
docker-compose up -d --build

# Forçar rebuild completo (sem cache)
docker-compose build --no-cache
docker-compose up -d
```

---

## 💾 Gerenciamento de Dados

### Banco de Dados

O banco de dados SQLite é armazenado em um **volume Docker** chamado `funnel-data`.

**Localização dentro do container:** `/app/data/funnel_builder.db`

### Backup do Banco

```bash
# Criar backup
docker-compose exec funnel-builder cp /app/data/funnel_builder.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db

# Copiar backup para o host
docker cp funnel-builder-app:/app/data/backup_*.db ./
```

### Restaurar Banco

```bash
# Copiar arquivo para o container
docker cp funnel_builder_backup.db funnel-builder-app:/app/data/funnel_builder.db

# Reiniciar aplicação
docker-compose restart
```

### Listar volumes

```bash
docker volume ls | grep funnel
```

### Inspecionar volume

```bash
docker volume inspect funnel-builder_funnel-data
```

---

## 🐛 Debugging

### Acessar shell do container

```bash
docker-compose exec funnel-builder bash
```

### Executar comandos Python

```bash
# Verificar banco de dados
docker-compose exec funnel-builder python -c "from database import db; print(db.get_stats())"

# Testar autenticação
docker-compose exec funnel-builder python auth.py

# Testar models
docker-compose exec funnel-builder python models.py
```

### Ver uso de recursos

```bash
docker stats funnel-builder-app
```

---

## 🔧 Configurações Avançadas

### Porta customizada

Edite `docker-compose.yml`:

```yaml
ports:
  - "3000:8000"  # HOST:CONTAINER
```

Depois rebuild:
```bash
docker-compose down
docker-compose up -d
```

### Modo desenvolvimento (hot-reload)

Descomente no `docker-compose.yml`:

```yaml
volumes:
  - .:/app  # Monta código fonte
```

**Nota:** Você precisará reiniciar o container manualmente após mudanças, pois o servidor HTTP não tem hot-reload.

### Variáveis de ambiente

Adicione no `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - DEBUG=true
  - DB_PATH=/app/data/custom.db
```

---

## 📊 Health Check

O container possui um health check configurado:

```bash
# Ver status do health check
docker inspect funnel-builder-app | grep -A 10 Health
```

**Parâmetros:**
- **Intervalo:** 30 segundos
- **Timeout:** 10 segundos
- **Retries:** 3
- **Start period:** 40 segundos

---

## 🌐 Produção

### Usando Nginx como proxy reverso

Crie `nginx.conf`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://funnel-builder:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Adicione ao `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - funnel-builder
```

### HTTPS com Let's Encrypt

Use [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) ou [Traefik](https://traefik.io/).

---

## 🧹 Limpeza

### Remover tudo (containers, volumes, imagens)

```bash
# CUIDADO: Isso apaga todos os dados!
docker-compose down -v --rmi all

# Remover imagens órfãs
docker image prune -a

# Remover volumes não usados
docker volume prune
```

---

## ❓ Troubleshooting

### Porta 8000 já está em uso

```bash
# Descobrir qual processo está usando
lsof -ti:8000

# Matar processo
lsof -ti:8000 | xargs kill -9

# Ou mude a porta no docker-compose.yml
```

### Container não inicia

```bash
# Ver logs completos
docker-compose logs

# Ver apenas erros
docker-compose logs 2>&1 | grep -i error
```

### Permissões do volume

```bash
# Acessar container como root
docker-compose exec -u root funnel-builder bash

# Corrigir permissões
chown -R 1000:1000 /app/data
```

### Banco de dados corrompido

```bash
# Remover banco e volumes
docker-compose down -v

# Reiniciar (cria novo banco limpo)
docker-compose up -d
```

---

## 📚 Referências

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)

---

## 🎯 Comandos Rápidos

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Rebuild
docker-compose up -d --build

# Backup
docker cp funnel-builder-app:/app/data/funnel_builder.db ./backup.db

# Shell
docker-compose exec funnel-builder bash

# Stats
docker stats funnel-builder-app
```

---

**Desenvolvido com** 🐳 Docker + 🐍 Python + ⚛️ React
