from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client

APP_ROOT = Path(__file__).parent
EBOOKS_DIR = APP_ROOT / "ebooks"
COMPONENT_DIR = APP_ROOT / "components" / "highlight_reader"

st.set_page_config(page_title="Leitor Med", page_icon="📚", layout="wide")

highlight_reader = components.declare_component("highlight_reader", path=str(COMPONENT_DIR))


# ---------------------------
# Utilidades
# ---------------------------

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
    # Identificador estável dos destaques.
    # Evite renomear/mover o arquivo depois que começar a destacar.
    return f"{area}/{file_path.name}"


def read_html(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="replace")


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


@st.cache_resource
def get_supabase() -> Optional[Client]:
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def load_highlights(doc_id: str, user_key: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    if not supabase:
        return []

    try:
        response = (
            supabase.table("highlights")
            .select("payload")
            .eq("user_key", user_key)
            .eq("document_id", doc_id)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return []
        payload = rows[0].get("payload") or []
        if isinstance(payload, str):
            return json.loads(payload)
        return payload
    except Exception as e:
        st.warning(f"Não consegui carregar os destaques do Supabase: {e}")
        return []


def save_highlights(doc_id: str, user_key: str, highlights: List[Dict[str, Any]]) -> bool:
    supabase = get_supabase()
    if not supabase:
        return False

    try:
        supabase.table("highlights").upsert(
            {
                "user_key": user_key,
                "document_id": doc_id,
                "payload": highlights,
            },
            on_conflict="user_key,document_id",
        ).execute()
        return True
    except Exception as e:
        st.error(f"Não consegui salvar os destaques no Supabase: {e}")
        return False


# ---------------------------
# Login simples
# ---------------------------

st.title("📚 Leitor Med")
st.caption("Biblioteca pessoal de ebooks em HTML com destaques salvos em nuvem.")

app_password = get_secret("APP_PASSWORD")
user_key = get_secret("USER_KEY", "regiane")

if app_password:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form("login_form"):
            senha = st.text_input("Senha do app", type="password")
            entrar = st.form_submit_button("Entrar")
        if entrar and senha == app_password:
            st.session_state.authenticated = True
            st.rerun()
        elif entrar:
            st.error("Senha incorreta.")
        st.stop()

else:
    st.info("Senha do app não configurada. Para proteger o acesso, configure APP_PASSWORD nos Secrets do Streamlit.")


# ---------------------------
# Sidebar
# ---------------------------

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
    st.caption("Dicas")
    st.markdown(
        """
        1. Selecione um trecho do texto.
        2. Clique em **Destacar seleção**.
        3. Para apagar, clique no destaque e use **Apagar selecionado**.
        4. Os destaques são salvos no Supabase.
        """
    )


# ---------------------------
# Leitor
# ---------------------------

html_content = read_html(ebook_path)
initial_highlights = load_highlights(doc_id, user_key)

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
            if save_highlights(doc_id, user_key, highlights):
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
            "Baixar JSON dos destaques",
            data=json.dumps(export_payload, ensure_ascii=False, indent=2),
            file_name=f"{ebook_path.stem}_destaques.json",
            mime="application/json",
        )

st.divider()
st.caption("Evite renomear ou mover um HTML depois de começar a destacar, pois os destaques ficam vinculados ao caminho do arquivo.")
