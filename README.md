# Ebook Internato

App em Streamlit para ler ebooks em HTML e destacar trechos.

## Esta versão

Esta versão foi simplificada:

- não usa senha;
- não usa usuário;
- não usa Supabase;
- salva os destaques em `data/highlights_store.json`.

## Como publicar no Streamlit

No Streamlit Community Cloud, configure:

- Repository: `leandro-cine/ebooks-internato`
- Branch: `main`
- Main file path: `app.py`

Não precisa preencher Secrets.

## Como adicionar ebooks

Coloque arquivos `.html` dentro de uma pasta de área em `ebooks/`.

Exemplo:

```text
ebooks/pediatria/PED 1 - Neonatologia I.html
ebooks/clinica_medica/Cardiologia.html
```

O app lista automaticamente as áreas e os ebooks.

## Importante sobre os destaques

Os destaques são salvos em `data/highlights_store.json` no ambiente onde o app está rodando.

No Streamlit Community Cloud, esse arquivo pode ser apagado quando o app reiniciar, quando você fizer redeploy ou quando atualizar o repositório. Por isso, o app tem botão para baixar backup dos destaques.

Para sincronização permanente entre dispositivos, o ideal continua sendo usar um banco externo, mas esta versão removeu essa etapa para simplificar.
