#!/bin/bash
# Script de diagnóstico para verificar fotos no servidor de produção
# Execute este script NO SERVIDOR DE PRODUÇÃO

echo "========================================="
echo "   DIAGNÓSTICO DE FOTOS - DASHBOARD"
echo "========================================="
echo ""

# 1. Verificar diretório atual
echo "📁 Diretório atual:"
pwd
echo ""

# 2. Verificar branch e último commit
echo "🌿 Branch e último commit:"
git branch
git log --oneline -1
echo ""

# 3. Verificar se pasta de fotos existe
echo "📂 Verificando pasta imagens/fotos/:"
if [ -d "imagens/fotos" ]; then
    echo "✅ Pasta existe"
    ls -lh imagens/fotos/
    echo ""
    echo "📊 Total de arquivos: $(ls imagens/fotos/ | wc -l)"
else
    echo "❌ Pasta NÃO existe!"
fi
echo ""

# 4. Verificar se fotos estão no git
echo "🔍 Fotos rastreadas pelo git:"
git ls-files imagens/fotos/
echo ""

# 5. Verificar status do repositório
echo "📋 Status do repositório:"
git status
echo ""

# 6. Verificar commit remoto vs local
echo "🌐 Comparação com GitHub:"
echo "Commit local:  $(git rev-parse HEAD)"
echo "Commit remoto: $(git ls-remote origin HEAD | cut -f1)"
echo ""

# 7. Verificar se há mudanças não commitadas
echo "⚠️  Verificando mudanças locais:"
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Repositório limpo (sem mudanças)"
else
    echo "⚠️  HÁ MUDANÇAS LOCAIS:"
    git status --short
fi
echo ""

# 8. Verificar permissões das fotos
echo "🔐 Permissões das fotos:"
if [ -d "imagens/fotos" ]; then
    ls -l imagens/fotos/*.png | head -3
fi
echo ""

# 9. Testar leitura de uma foto
echo "🖼️  Testando leitura de foto:"
if [ -f "imagens/fotos/1.png" ]; then
    file imagens/fotos/1.png
    echo "✅ Foto 1.png acessível"
else
    echo "❌ Foto 1.png NÃO encontrada!"
fi
echo ""

echo "========================================="
echo "   FIM DO DIAGNÓSTICO"
echo "========================================="
echo ""
echo "🔧 AÇÕES RECOMENDADAS:"
echo ""
echo "Se as fotos NÃO existem no servidor:"
echo "  → git pull origin master"
echo ""
echo "Se há mudanças locais bloqueando o pull:"
echo "  → git stash"
echo "  → git pull origin master"
echo ""
echo "Se o commit local está desatualizado:"
echo "  → git fetch origin"
echo "  → git reset --hard origin/master"
echo ""
