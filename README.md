# Meu Financeiro — Sistema de Gerenciamento Financeiro Pessoal

Aplicação web desenvolvida com Django para organizar receitas, despesas, categorias, metas e relatórios pessoais. Possui login tradicional e integração opcional com Google OAuth 2.0.

## Funcionalidades

- Cadastro, login e logout por usuário.
- Login com Google usando `django-allauth`.
- Dashboard com **um único saldo geral**, calculado pela soma de todas as receitas menos todas as despesas.
- Cadastro, edição, exclusão, busca e filtro de receitas e despesas.
- Categorias padrão criadas automaticamente para cada usuário.
- Cadastro e acompanhamento de metas financeiras.
- Relatório anual de receitas e despesas por mês.
- Dados isolados por usuário: cada pessoa acessa somente suas próprias transações, categorias e metas.

> **Não é necessário cadastrar conta bancária, carteira ou cartão.** O aplicativo trabalha com um único saldo geral. Basta lançar receitas e despesas; o dashboard calcula o saldo automaticamente.

## Categorias criadas automaticamente

Na primeira visita ao dashboard, o sistema cria as categorias padrão que ainda não existirem para aquele usuário. Elas também aparecem na tela Categorias e podem ser complementadas com categorias personalizadas.

**Receitas:** Salário, Freelance, Investimentos, Vendas, Renda extra, Reembolso e Outras receitas.

**Despesas:** Moradia, Alimentação, Transporte, Saúde, Educação, Lazer, Compras, Contas e serviços, Assinaturas, Impostos e taxas, Cuidados pessoais, Pets, Viagens, Presentes e doações e Outras despesas.

As categorias são individuais por usuário. Um usuário pode renomear, excluir ou criar categorias sem afetar os demais. Uma categoria de receita não pode ser usada em uma despesa, nem o contrário.

## Tecnologias

- Python 3.12 ou superior (recomendado Python 3.13/3.14)
- Django 6
- django-allauth
- SQLite (banco local padrão)
- HTML e CSS

## 1. Preparar o ambiente (Windows)

Extraia o ZIP e abra no VS Code a pasta `financeiro_pessoal`, que contém o arquivo `manage.py`.

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative no PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Ou no Prompt de Comando (CMD):

```bat
venv\Scripts\activate.bat
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configurar o ambiente

Copie `.env.example` e renomeie a cópia para `.env`:

```powershell
Copy-Item .env.example .env
```

Para usar somente login e senha, deixe as variáveis do Google vazias. O login Google será habilitado quando as credenciais forem preenchidas.

## 3. Configurar login com Google (opcional)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/) e selecione seu projeto.
2. Abra [Google Auth Platform](https://console.cloud.google.com/auth/overview).
3. Em **Branding**, informe o nome do aplicativo e o e-mail de suporte.
4. Em **Audience**, escolha **External** e, enquanto estiver testando, adicione seu Gmail em **Test users**.
5. Em **Clients**, crie um cliente OAuth do tipo **Web application**.
6. Em **Authorized JavaScript origins**, adicione `http://127.0.0.1:8000`.
7. Em **Authorized redirect URIs**, adicione exatamente `http://127.0.0.1:8000/accounts/google/login/callback/`.
8. Copie o Client ID e o Client Secret para o arquivo `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=sua-chave-secreta
```

Salve o `.env` e reinicie o servidor. Use `http://127.0.0.1:8000` no navegador para que o endereço corresponda ao cadastrado no Google. Não publique o `.env` nem compartilhe o Client Secret.

## 4. Criar o banco e iniciar o sistema

O projeto já inclui a migração inicial. Com o ambiente virtual ativado, execute:

```bash
python manage.py migrate
python manage.py check
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

Crie uma conta pela tela de cadastro ou entre com Google. Ao abrir o dashboard pela primeira vez, o sistema prepara automaticamente as categorias padrão.

Para acessar o painel administrativo do Django, crie um superusuário:

```bash
python manage.py createsuperuser
```

Depois acesse `http://127.0.0.1:8000/admin/`.

## 5. Como o saldo geral funciona

O saldo geral não depende de uma conta bancária cadastrada:

`Saldo geral = soma das receitas - soma das despesas`

Exemplo:

- Receitas lançadas: R$ 5.000,00
- Despesas lançadas: R$ 1.750,00
- Saldo geral: R$ 3.250,00

O cálculo considera todas as transações registradas pelo usuário. O resultado mensal é calculado separadamente, considerando apenas o mês atual.

## 6. Regras de negócio

- Cada transação, categoria e meta pertence a um usuário.
- Um usuário não pode consultar, editar ou excluir dados de outro usuário pelas telas da aplicação.
- O valor de uma transação deve ser maior que zero.
- Uma categoria de receita só pode ser usada em uma receita; uma categoria de despesa só pode ser usada em uma despesa.
- A parcela atual não pode ser maior que o número total de parcelas.
- O saldo geral é calculado automaticamente pelas receitas menos despesas; não existe cadastro de conta bancária.
- As categorias padrão são criadas automaticamente, sem duplicar categorias já existentes para o usuário.
- O progresso da meta é calculado automaticamente e limitado a 100%.

## Observações importantes

- O banco SQLite é criado localmente após `migrate`.
- Se você estiver atualizando a versão anterior, faça uma cópia de segurança de `db.sqlite3`, substitua os arquivos pelo conteúdo deste ZIP e execute `python manage.py migrate`. A migração `0002` remove a antiga estrutura de contas bancárias e mantém as transações existentes.
- O login Google depende de credenciais OAuth criadas pelo responsável pelo projeto; elas não acompanham o ZIP.
- O campo de parcelamento registra a parcela atual e o total de parcelas, mas não gera automaticamente lançamentos futuros.
- Esta é uma aplicação didática. Antes de publicar na internet, configure `DEBUG=False`, uma `DJANGO_SECRET_KEY` forte, hosts permitidos, HTTPS, banco de produção, backups e política de privacidade.
