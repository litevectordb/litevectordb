#!/bin/bash
# Script para limpar o repositório GitHub e resubmeter os arquivos atuais

set -e

echo "🚨 ATENÇÃO: Este script vai APAGAR tudo no repositório remoto e substituir!"
echo "Repositório: $(git remote get-url origin)"
echo ""
read -p "Continuar? (sim/não): " confirm

if [ "$confirm" != "sim" ]; then
    echo "❌ Cancelado."
    exit 1
fi

echo ""
echo "📦 Adicionando todos os arquivos..."
git add -A

echo "💾 Criando commit com a estrutura reorganizada..."
git commit -m "Reorganiza estrutura do pacote: move arquivos para litevectordb/" || echo "⚠️  Nenhuma mudança para commitar"

echo ""
echo "🗑️  Limpando histórico remoto e enviando nova estrutura..."
echo "⚠️  Isso vai substituir TUDO no branch main do repositório remoto!"

# Opção 1: Criar branch orphan (histórico completamente limpo)
echo ""
echo "Escolha uma opção:"
echo "1) Criar histórico completamente novo (recomendado para limpar tudo)"
echo "2) Fazer force push simples (substitui o branch atual)"
read -p "Opção (1 ou 2): " option

if [ "$option" == "1" ]; then
    echo "🔄 Criando branch orphan..."
    git checkout --orphan new_main
    git add -A
    git commit -m "Initial commit: LiteVectorDB package structure"
    git branch -D main
    git branch -m main
    git push -f origin main
    echo "✅ Histórico limpo e novo conteúdo enviado!"
elif [ "$option" == "2" ]; then
    echo "🔄 Fazendo force push..."
    git push -f origin main
    echo "✅ Conteúdo enviado com sucesso!"
else
    echo "❌ Opção inválida. Cancelado."
    exit 1
fi

echo ""
echo "✅ Pronto! O repositório remoto foi atualizado."
echo "📝 Você pode verificar em: $(git remote get-url origin)"

