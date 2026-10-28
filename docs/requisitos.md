# Requisitos do MVP

## Funcionais
- RF01 (Obrigatório): login com perfis de coordenação e voluntário
- RF02 (Obrigatório): cadastro de famílias com aviso de duplicidade
- RF03 (Obrigatório): registro de retirada, uma por família por mês
- RF04 (Obrigatório): entradas de doação e saldo de estoque calculado
- RF05 (Desejável): alerta de estoque baixo
- RF06 (Desejável): relatório mensal em PDF
- RF07 (Desejável): retirada offline com sincronização

## Não funcionais
- RNF01: autenticação com hash de senha (PBKDF2) e sessão segura
- RNF02: controles alinhados ao OWASP (validação no servidor, ORM, escape de saída)
- RNF03: hospedagem de baixo custo e carregamento em até 3 segundos
- RNF04: acessibilidade (botões de 44 px ou mais, contraste, alertas com texto e símbolo)
