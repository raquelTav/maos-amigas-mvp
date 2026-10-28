# Mãos Amigas MVP

Sistema web simples para a Associação Mãos Amigas (Bairro Bom Jardim, Fortaleza-CE)
controlar o cadastro de famílias, a retirada mensal de cestas básicas e o estoque.

## Problema
O controle é feito em cadernos e em uma planilha desatualizada, o que gera
cadastros duplicados, estoque desconhecido e relatórios demorados.

## Funcionalidades do MVP
- RF01: login com perfis (coordenação e voluntário)
- RF02: cadastro de famílias com aviso de duplicidade
- RF03: registro de retirada (uma por família por mês)
- RF04: entradas de doação e saldo de estoque
- RF05 (desejável): alerta de estoque baixo
- RF06 (desejável): relatório mensal em PDF
- RF07 (desejável): retirada offline com sincronização

## Tecnologias
Python 3.12, Django 5.2 LTS, PostgreSQL, psycopg 3, ReportLab, Bootstrap 5.3.

## Arquitetura
Monólito em três camadas: apresentação (templates), regras de negócio (serviços)
e acesso a dados (ORM do Django).

## Como executar (desenvolvimento)
1. Criar ambiente virtual e instalar `requirements.txt`
2. Definir as variáveis de ambiente (veja `.env.example`)
3. Rodar `python manage.py migrate`
4. Rodar `python manage.py runserver`

## Estrutura do repositório
- docs/: requisitos e documentação do projeto
- prototipo_maos_amigas.html: protótipo das três telas
- requirements.txt: dependências Python
- .env.example: modelo das variáveis de ambiente (sem valores reais)

## Como executar (em desenvolvimento)
1. Criar um ambiente virtual e instalar `requirements.txt`
2. Copiar `.env.example` para `.env` e preencher os valores
3. Executar as migrações do banco e iniciar o servidor

## Status
Em desenvolvimento. Protótipo e plano de validação concluídos.

## Autoria
Raquel Araujo Tavares. Projeto acadêmico de Análise e Desenvolvimento de Sistemas.
