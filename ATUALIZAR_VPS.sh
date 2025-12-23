#!/bin/bash

# Script de atualização automática do Funnel Builder na VPS
# Execute este script para atualizar para a versão mais recente

echo "🔄 Atualizando Funnel Builder para v1.0.0..."
echo ""

# Salva mudanças locais
echo "📦 Salvando mudanças locais..."
git stash

# Atualiza do GitHub
echo "⬇️ Baixando última versão do GitHub..."
git fetch --all
git reset --hard origin/main

# Verifica versão
echo ""
echo "✅ Versão atual:"
git log -1 --oneline

# Verifica se tem os arquivos novos
echo ""
echo "🔍 Verificando arquivos novos..."
if grep -q "analyzeBottlenecks" funnel_builder.py; then
    echo "✅ Análise de gargalos: OK"
else
    echo "❌ Análise de gargalos: NÃO ENCONTRADA"
fi

if [ -f "UPDATE_INSTRUCTIONS.md" ]; then
    echo "✅ Instruções de atualização: OK"
else
    echo "❌ Instruções de atualização: NÃO ENCONTRADAS"
fi

if grep -q "Gerenciamento de Marketing Digital" README.md; then
    echo "✅ Seção de Marketing no README: OK"
else
    echo "❌ Seção de Marketing no README: NÃO ENCONTRADA"
fi

# Instala dependências
echo ""
echo "📦 Verificando dependências..."
pip3 install bcrypt 2>/dev/null && echo "✅ bcrypt instalado"

echo ""
echo "🎉 Atualização concluída!"
echo ""
echo "Para reiniciar o servidor:"
echo "  killall python3"
echo "  python3 funnel_builder.py"
