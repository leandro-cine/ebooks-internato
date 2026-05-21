from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components

APP_ROOT = Path(__file__).parent
EBOOKS_DIR = APP_ROOT / "ebooks"
COMPONENT_DIR = APP_ROOT / "components" / "highlight_reader"
DATA_DIR = APP_ROOT / "data"
DATA_FILE = DATA_DIR / "highlights_store.json"

st.set_page_config(page_title="Ebook Internato", page_icon="📚", layout="wide")

highlight_reader = components.declare_component("highlight_reader", path=str(COMPONENT_DIR))

AREA_LABELS = {
    "pediatria": "Pediatria",
    "clinica_medica": "Clínica Médica",
    "ginecologia_obstetricia": "Ginecologia e Obstetrícia",
    "cirurgia": "Cirurgia",
    "preventiva": "Preventiva / Saúde Coletiva",
}


def slug_to_label(slug: str) -> str:
    return AREA_LABELS.get(slug, slug.replace("_", " ").title())


def clean_title(filename: str) -> str:
    title = Path(filename).stem
    title = re.sub(r"[_\-]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def list_areas() -> List[str]:
    if not EBOOKS_DIR.exists():
        return []
    return sorted([p.name for p in EBOOKS_DIR.iterdir() if p.is_dir()])


def list_html_files(area: str) -> List[Path]:
    area_dir = EBOOKS_DIR / area
    if not area_dir.exists():
        return []
    return sorted(area_dir.glob("*.html"), key=lambda p: p.name.lower())


def document_id(area: str, file_path: Path) -> str:
    # Identificador do documento. Evite renomear/mover o HTML depois de destacar.
    return f"{area}/{file_path.name}"


def read_html(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="replace")


def ensure_data_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def read_store() -> Dict[str, List[Dict[str, Any]]]:
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_store(store: Dict[str, List[Dict[str, Any]]]) -> None:
    ensure_data_file()
    DATA_FILE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def load_highlights(doc_id: str) -> List[Dict[str, Any]]:
    store = read_store()
    highlights = store.get(doc_id, [])
    return highlights if isinstance(highlights, list) else []


def save_highlights(doc_id: str, highlights: List[Dict[str, Any]]) -> bool:
    try:
        store = read_store()
        store[doc_id] = highlights
        write_store(store)
        return True
    except Exception as e:
        st.error(f"Não consegui salvar os destaques no arquivo local: {e}")
        return False


def all_highlights_payload() -> Dict[str, Any]:
    store = read_store()
    return {
        "app": "ebook-internato",
        "storage": "local-json",
        "highlights_by_document": store,
    }


st.title("📚 Ebook Internato")
st.caption("Biblioteca de ebooks em HTML com destaques salvos em arquivo local do app.")

st.info(
    "Versão simplificada: sem senha, sem usuário e sem Supabase. "
    "Os destaques são gravados no arquivo `data/highlights_store.json` dentro do app."
)

with st.sidebar:
    st.header("Biblioteca")

    areas = list_areas()
    if not areas:
        st.error("Nenhuma área encontrada dentro da pasta ebooks/.")
        st.stop()

    area = st.selectbox(
        "Área",
        areas,
        format_func=slug_to_label,
        index=areas.index("pediatria") if "pediatria" in areas else 0,
    )

    html_files = list_html_files(area)
    if not html_files:
        st.warning("Nenhum arquivo .html encontrado nesta área.")
        st.stop()

    ebook_path = st.selectbox(
        "Ebook",
        html_files,
        format_func=lambda p: clean_title(p.name),
    )

    doc_id = document_id(area, ebook_path)

    st.divider()
    st.caption("Documento selecionado")
    st.code(doc_id)

    st.divider()
    st.caption("Como destacar")
    st.markdown(
        """
        1. Selecione um trecho do texto.
        2. Clique em **Destacar seleção**.
        3. Para apagar, clique no destaque e use **Apagar selecionado**.
        4. Os destaques são salvos automaticamente no app.
        """
    )

    st.divider()
    st.caption("Backup")
    st.download_button(
        "Baixar todos os destaques",
        data=json.dumps(all_highlights_payload(), ensure_ascii=False, indent=2),
        file_name="backup_todos_os_destaques.json",
        mime="application/json",
    )

html_content = read_html(ebook_path)
initial_highlights = load_highlights(doc_id)

col1, col2 = st.columns([0.72, 0.28], gap="large")

with col1:
    st.subheader(clean_title(ebook_path.name))

    component_value = highlight_reader(
        html=html_content,
        highlights=initial_highlights,
        doc_id=doc_id,
        key=f"reader-{doc_id}",
        height=820,
    )

    if component_value and isinstance(component_value, dict):
        event = component_value.get("event")
        highlights = component_value.get("highlights", [])

        if event in {"changed", "delete_all", "delete_selected"}:
            if save_highlights(doc_id, highlights):
                st.toast("Destaques salvos.", icon="✅")
                st.session_state[f"last_highlights_{doc_id}"] = highlights

with col2:
    st.subheader("Meus destaques")

    highlights_for_panel = st.session_state.get(f"last_highlights_{doc_id}", initial_highlights)

    if not highlights_for_panel:
        st.info("Você ainda não destacou trechos neste ebook.")
    else:
        st.write(f"Total: **{len(highlights_for_panel)}**")
        for i, h in enumerate(highlights_for_panel, start=1):
            text = h.get("text", "").strip()
            color = h.get("color", "yellow")
            st.markdown(f"**{i}.** `{color}`")
            st.write(text[:700] + ("..." if len(text) > 700 else ""))
            st.divider()

    with st.expander("Exportar destaques deste ebook"):
        export_payload = {
            "document_id": doc_id,
            "ebook": clean_title(ebook_path.name),
            "area": slug_to_label(area),
            "highlights": highlights_for_panel,
        }
        st.download_button(
            "Baixar JSON deste ebook",
            data=json.dumps(export_payload, ensure_ascii=False, indent=2),
            file_name=f"{ebook_path.stem}_destaques.json",
            mime="application/json",
        )

st.divider()
st.caption(
    "Observação: no Streamlit Community Cloud, arquivos gravados pelo app podem ser perdidos em reinicializações, "
    "redeploys ou atualizações do repositório. Use o botão de backup se quiser guardar uma cópia dos destaques."
)
