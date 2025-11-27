# 📋 Recomendação: Pastas /api e /examples

## ✅ Pode Remover Ambas

**Sim, você pode remover ambas as pastas antes de distribuir!**

### Por quê?

1. **Não são instaladas**: Essas pastas não estão no `packages` do `pyproject.toml`, então não serão incluídas quando alguém faz `pip install litevectordb`

2. **Exemplos já documentados**: O README.md já contém todos os exemplos de uso necessários

3. **API é projeto separado**: A pasta `/api` contém uma API REST completa (FastAPI), que é um projeto separado do pacote principal

## 🎯 Recomendações por Cenário

### Cenário 1: Pacote Limpo (Recomendado)
```bash
# Remove ambas
rm -rf api/ examples/
```

**Vantagens:**
- Projeto mais limpo e focado
- Menos confusão sobre o que é parte do pacote
- API pode ser um repositório separado

### Cenário 2: Manter Exemplos no Repositório
```bash
# Remove apenas /api
rm -rf api/
# Mantém /examples para quem clonar o repo
```

**Vantagens:**
- Exemplos disponíveis para quem clonar do GitHub
- Útil para contribuidores

### Cenário 3: Manter Tudo
```bash
# Não remove nada
```

**Vantagens:**
- Tudo disponível no repositório
- API REST como exemplo de uso avançado

## 💡 Minha Recomendação

**Remover ambas as pastas** porque:

1. ✅ O README.md já tem exemplos completos
2. ✅ A API REST pode ser um projeto separado
3. ✅ Mantém o pacote focado e limpo
4. ✅ Usuários podem ver exemplos no README sem precisar clonar

Se quiser manter exemplos no repositório, mantenha apenas `/examples` (que tem apenas 1 arquivo simples).

