from pathlib import Path
from ftfy import fix_text
import re
import shutil

# Pasta onde estão os arquivos HTML
pasta = Path(".")

# Pasta onde serão salvos os arquivos corrigidos
pasta_saida = pasta / "html_corrigidos"
pasta_saida.mkdir(exist_ok=True)

# Pasta de backup dos originais
pasta_backup = pasta / "backup_originais"
pasta_backup.mkdir(exist_ok=True)

codificacoes = ["utf-8", "cp1252", "latin1", "iso-8859-1"]

def pontuar_texto(texto):
    """
    Quanto menor a pontuação, melhor.
    Penaliza sinais típicos de erro de codificação.
    """
    sinais_ruins = ["Ã", "Â", " ", "â€™", "â€œ", "â€", "¤", "œ", "€"]
    pontos = 0

    for sinal in sinais_ruins:
        pontos += texto.count(sinal) * 10

    # Penaliza interrogação suspeita no meio de palavras
    pontos += len(re.findall(r"[A-Za-zÀ-ÿ]\?[A-Za-zÀ-ÿ]", texto)) * 10

    return pontos

def corrigir_html(arquivo):
    conteudo_bytes = arquivo.read_bytes()

    melhor_texto = None
    melhor_pontuacao = float("inf")
    melhor_codificacao = None

    for codificacao in codificacoes:
        try:
            texto = conteudo_bytes.decode(codificacao, errors="replace")
            texto_corrigido = fix_text(texto)

            pontuacao = pontuar_texto(texto_corrigido)

            if pontuacao < melhor_pontuacao:
                melhor_texto = texto_corrigido
                melhor_pontuacao = pontuacao
                melhor_codificacao = codificacao

        except Exception:
            pass

    corrigido = melhor_texto

    # Corrige marcadores de lista que viraram "?"
    corrigido = re.sub(r"(?m)^(\s*)\?\s+", r"\1• ", corrigido)
    corrigido = re.sub(r">\s*\?\s+", ">• ", corrigido)

    # Garante charset UTF-8 no HTML
    corrigido = re.sub(
        r'<meta\s+charset=["\']?[^"\'>]+["\']?\s*/?>',
        '<meta charset="UTF-8">',
        corrigido,
        flags=re.IGNORECASE
    )

    # Se não existir meta charset, adiciona dentro do <head>
    if '<meta charset="UTF-8">' not in corrigido and "<head>" in corrigido.lower():
        corrigido = re.sub(
            r"<head>",
            '<head>\n<meta charset="UTF-8">',
            corrigido,
            count=1,
            flags=re.IGNORECASE
        )

    return corrigido, melhor_codificacao, melhor_pontuacao

# Pega todos os arquivos .html da pasta atual
arquivos_html = list(pasta.glob("*.html"))

if not arquivos_html:
    print("Nenhum arquivo .html encontrado nesta pasta.")
else:
    print(f"{len(arquivos_html)} arquivo(s) HTML encontrado(s).\n")

for arquivo in arquivos_html:
    print(f"Corrigindo: {arquivo.name}")

    # Salva backup do original
    backup = pasta_backup / arquivo.name
    if not backup.exists():
        shutil.copy2(arquivo, backup)

    corrigido, codificacao, pontuacao = corrigir_html(arquivo)

    # Salva na pasta html_corrigidos com o mesmo nome
    arquivo_corrigido = pasta_saida / arquivo.name
    arquivo_corrigido.write_text(corrigido, encoding="utf-8")

    print(f"  Codificação escolhida: {codificacao}")
    print(f"  Pontuação de problemas restantes: {pontuacao}")
    print(f"  Salvo em: {arquivo_corrigido}")
    print()

print("Processo finalizado.")
print("Os originais foram preservados em: backup_originais")
print("Os corrigidos foram salvos em: html_corrigidos")