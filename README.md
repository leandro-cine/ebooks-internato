# Leitor Med — Streamlit + HTML + Destaques em Nuvem

Este projeto cria uma biblioteca pessoal de ebooks médicos em HTML, organizada por áreas, com destaque de trechos e salvamento em nuvem via Supabase.

## Estrutura

```text
app.py
requirements.txt
database_supabase.sql
.streamlit/
  config.toml
  secrets.toml.example
components/
  highlight_reader/
    index.html
ebooks/
  pediatria/
    PED 1 - Neonatologia I.html
    PED 1 - Neonatologia II.html
    PED 2 - Aleitamento Materno.html
    ...
  clinica_medica/
  ginecologia_obstetricia/
  cirurgia/
  preventiva/
tools/
  corrigir_todos_html.py
```

## Como colocar novos ebooks

Coloque os arquivos `.html` dentro da pasta da área correspondente.

Exemplos:

```text
ebooks/pediatria/Meu Ebook.html
ebooks/clinica_medica/Cardiologia.html
ebooks/ginecologia_obstetricia/Pré-natal.html
```

Evite renomear/mover um HTML depois que começar a destacar, pois os destaques ficam vinculados ao caminho do arquivo.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para testar com Supabase localmente, crie o arquivo:

```text
.streamlit/secrets.toml
```

com:

```toml
APP_PASSWORD = "sua-senha"
USER_KEY = "regiane"

SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_KEY = "SUA-CHAVE"
```

## Criar banco no Supabase

1. Acesse seu projeto no Supabase.
2. Vá em **SQL Editor**.
3. Cole o conteúdo de `database_supabase.sql`.
4. Clique em **Run**.

## Publicar no Streamlit Community Cloud

1. Suba este projeto para o GitHub.
2. Acesse o Streamlit Community Cloud.
3. Clique em **Create app**.
4. Escolha o repositório.
5. Em **Main file path**, coloque:

```text
app.py
```

6. Em **Settings > Secrets**, cole:

```toml
APP_PASSWORD = "sua-senha"
USER_KEY = "regiane"

SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_KEY = "SUA-CHAVE"
```

## Como usar

1. Abra o app.
2. Digite a senha.
3. Escolha a área.
4. Escolha o ebook.
5. Selecione um trecho.
6. Clique em **Destacar seleção**.
7. O destaque será salvo no Supabase e aparecerá em outros dispositivos.

## Observação

Esta versão salva os destaques por posição de texto. Se o HTML for muito alterado depois, os destaques podem deslocar.
