# 🔄 Instruções de Atualização - Funnel Builder

## Para o Claude na VPS

Execute os seguintes comandos na ordem exata:

### 1️⃣ Navegue até o diretório do projeto
```bash
cd /caminho/para/funnel-builder
```

### 2️⃣ Verifique o status atual
```bash
git status
git branch
```

### 3️⃣ Salve mudanças locais (se houver)
```bash
git stash
```

### 4️⃣ Force atualização do repositório
```bash
git fetch origin
git reset --hard origin/main
```

### 5️⃣ Verifique a versão atualizada
```bash
git log --oneline -5
```

### 6️⃣ Instale dependências (se necessário)
```bash
pip3 install bcrypt
```

### 7️⃣ Reinicie o servidor
```bash
# Mate processos antigos
killall python3 funnel_builder.py 2>/dev/null || true

# Inicie o novo servidor
python3 funnel_builder.py
```

---

## ✅ Última Versão (Commit: efea92d)

**Data:** Dezembro 2024

**Mudanças principais:**
- ✅ Sistema de análise de gargalos
- ✅ Duplicação de funis
- ✅ Gerenciamento completo de marketing digital (páginas + UTMs)
- ✅ Bug de validação de URL corrigido
- ✅ Documentação consolidada no README.md
- ✅ 7 arquivos de documentação obsoletos removidos

**Arquivos removidos:**
- API_DOCUMENTATION.md
- IMPLEMENTACAO_COMPLETA.md
- MARKETING_API.md
- PROMPT_PROJETO.md
- README.Docker.md
- SECURITY_IMPROVEMENTS.md
- SECURITY_PLAN.md

**Novos recursos:**
- Análise de gargalos do funil
- Duplicar funis existentes
- Cadastro de páginas de marketing
- Gerador de UTMs integrado
- Vincular páginas aos elementos do funil

---

## 🆘 Se ainda não atualizar

### Opção 1: Clone fresh
```bash
cd /caminho/pai/
rm -rf funnel-builder
git clone https://github.com/rodrigosaracino/funnel-builder.git
cd funnel-builder
pip3 install bcrypt
python3 funnel_builder.py
```

### Opção 2: Verifique a branch
```bash
git checkout main
git pull origin main --force
```

### Opção 3: Reset completo
```bash
git fetch --all
git reset --hard origin/main
git clean -fd
```

---

## 📊 Como verificar se está na versão correta

Execute:
```bash
git log -1 --oneline
```

Deve mostrar:
```
efea92d Higienização completa do código - remove docs obsoletos e corrige bugs
```

Ou verifique se existe a análise de gargalos:
```bash
grep -n "analyzeBottlenecks" funnel_builder.py
```

Deve retornar linhas com a função.

---

## 🔍 Debug

Se o problema persistir, verifique:

1. **Está no repositório correto?**
```bash
git remote -v
```

Deve mostrar: `https://github.com/rodrigosaracino/funnel-builder.git`

2. **Está na branch main?**
```bash
git branch
```

Deve mostrar: `* main`

3. **Tem mudanças locais conflitantes?**
```bash
git status
```

Se sim, use `git stash` ou `git reset --hard`

4. **Cache do git?**
```bash
git reflog
git gc --prune=now
```
