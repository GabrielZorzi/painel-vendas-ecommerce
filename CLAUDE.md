# Painel de Vendas Automático para E-commerce

## Contexto
Projeto demonstrativo de portfólio (freelance). Cenário: uma loja online extrai as vendas
do sistema todo dia, cola numa planilha e monta o relatório à mão. A solução automatiza
extração, tratamento e carga, e o gestor abre um dashboard sempre atualizado.

Dados: dataset público "Brazilian E-Commerce Public Dataset by Olist" (Kaggle), com os
CSVs salvos em `data/raw/`. Nada de dados reais de clientes ou de empregadores.

## Stack
- Python 3.12, gerenciado com uv (`uv add`, `uv run`). Nunca use pip diretamente.
- pandas para tratamento
- Postgres no Supabase (plano gratuito) como destino
- GitHub Actions para agendamento diário
- Looker Studio para o dashboard
- pytest para testes

## Estrutura
- `src/painel_vendas_ecommerce/` — código (extract, transform, load, config)
- `tests/` — testes com pytest
- `data/raw/` — CSVs originais (fora do Git)
- `data/processed/` — saídas intermediárias (fora do Git)

## Regras
- Trabalhe em tarefas pequenas. Antes de escrever código, proponha um plano curto e
  espere minha aprovação.
- Depois de cada mudança, explique o que fez e por quê, em português e de forma
  didática: estou fortalecendo minha base de Python, HTTP/APIs e POO.
- Não adicione dependências sem perguntar.
- Código com type hints e funções pequenas e testáveis. Nomes no código em inglês;
  README e explicações em português.
- Segredos (credenciais do Supabase) só em `.env`, que fica fora do Git. Mantenha um
  `.env.example` atualizado.
- Nunca commite arquivos de `data/`.
- Toda função de transformação nova ganha pelo menos um teste.

## Fora do escopo
- Front-end próprio (o dashboard é no Looker Studio)
- Dados em tempo real
- Machine learning
