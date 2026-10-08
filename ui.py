from pathlib import Path

import streamlit as st

from app.ingestion.document_router import load_document
from app.ingestion.chunker import chunk_documents
from app.ingestion.index_documents import index_documents
from app.retrieval.vector_store import add_documents_to_vector_store
from app.graph.workflow import build_graph
from app.organizations import (
    create_organization,
    get_organization,
    list_organizations,
    organization_raw_dir,
)


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="EnterpriseIQ",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".csv",
    ".xlsx",
    ".xls",
}


# ============================================================
# SESSION STATE
# ============================================================

_DEFAULTS = {
    "step": "orgs",
    "org_id": None,
    "graph": None,
    "last_result": None,
    "question_box": "",
    "uploaded_names": [],
}

for _key, _value in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_documents(org_id: str):
    """Return supported documents for one organization."""
    raw_dir = organization_raw_dir(org_id)

    return sorted(
        [
            file
            for file in raw_dir.iterdir()
            if file.is_file()
            and file.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda x: x.name.lower(),
    )


def get_graph():
    """Create the LangGraph workflow once per Streamlit session."""
    if st.session_state.graph is None:
        st.session_state.graph = build_graph()

    return st.session_state.graph


def run_question(question: str, org_id: str, allowed_sources=None):
    """Run the LangGraph workflow for one organization."""
    graph = get_graph()

    return graph.invoke(
        {
            "question": question,
            "retry_count": 0,
            "org_id": org_id,
            "allowed_sources": allowed_sources,
        }
    )


def index_single_document(file_path: Path, org_id: str):

    status = st.empty()
    progress = st.progress(0)

    try:

        status.info(
            f"Loading {file_path.name}..."
        )

        documents = load_document(
            str(file_path)
        )

        progress.progress(0.2)

        if not documents:

            status.error(
                f"No content found in {file_path.name}."
            )

            return False

        status.info(
            f"Chunking {file_path.name}..."
        )

        chunks = chunk_documents(
            documents
        )

        progress.progress(0.4)

        status.info(
            f"Embedding {len(chunks):,} chunks..."
        )

        add_documents_to_vector_store(
            chunks,
            org_id,
            batch_size=256,
        )

        progress.progress(1.0)

        status.success(
            f"✓ {file_path.name} indexed "
            f"({len(chunks):,} chunks)."
        )

        return True

    except Exception as exc:

        progress.empty()

        status.error(
            f"Failed to index {file_path.name}: {exc}"
        )

        return False


def select_organization(org_id: str):
    st.session_state.org_id = org_id
    st.session_state.step = "upload"
    st.session_state.uploaded_names = []
    st.session_state.last_result = None
    st.session_state.last_question = ""


def go_to_orgs():
    st.session_state.step = "orgs"
    st.session_state.org_id = None


def go_to_upload():
    st.session_state.step = "upload"


def go_to_query():
    st.session_state.step = "query"


def render_sources(sources):
    """Display evidence returned by the graph."""

    if not sources:
        st.info(
            "No evidence sources returned."
        )
        return

    for index, source in enumerate(
        sources,
        start=1,
    ):

        filename = Path(
            source.get(
                "source",
                "Unknown",
            )
        ).name

        metadata = []

        if source.get("page") is not None:
            metadata.append(
                f"Page {source['page']}"
            )

        if source.get("section"):
            metadata.append(
                f"Section: {source['section']}"
            )

        if source.get("sheet"):
            metadata.append(
                f"Sheet: {source['sheet']}"
            )

        if source.get("row") is not None:
            metadata.append(
                f"Row: {source['row']}"
            )

        if source.get("retrieval_score") is not None:
            metadata.append(
                f"Score: {source['retrieval_score']:.3f}"
            )

        with st.expander(
            f"📄 Source {index}: {filename}",
            expanded=index == 1,
        ):

            if metadata:

                st.caption(
                    " • ".join(metadata)
                )

            st.write(
                source.get(
                    "content",
                    "",
                )
            )


def render_result(result):
    """Display final LangGraph result."""

    if not result:
        return

    has_conflict = result.get(
        "has_conflict",
        False,
    )

    evidence_sufficient = result.get(
        "evidence_sufficient",
        False,
    )

    sources = result.get(
        "sources",
        [],
    )

    conflicts = result.get(
        "conflicts",
        [],
    )

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    answer = result.get("answer")
    llm_error = result.get("llm_error")

    if answer:
        st.subheader("💬 Answer")

        with st.container(border=True):
            st.markdown(answer)
    elif llm_error == "not_configured":
        st.caption(
            "AI answers are off (no GEMINI_API_KEY set). "
            "Showing matching passages only."
        )
    elif llm_error == "quota_exceeded":
        st.warning(
            "Gemini quota or rate limit exceeded — try again later. "
            "Showing matching passages only."
        )
    elif llm_error:
        st.warning(
            "The AI answer could not be generated. "
            "Showing matching passages only."
        )
        with st.expander("Error details"):
            st.code(llm_error)

    # --------------------------------------------------------
    # SOURCES & EVIDENCE (shown below the answer, with space)
    # --------------------------------------------------------

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()

    st.subheader("📚 Sources & evidence")

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        if evidence_sufficient:
            st.success(f"✓ {len(sources)} passage(s) found")
        else:
            st.error("✗ No matching passages found")

    with status_col2:

        if has_conflict:
            st.error("⚠ Conflict Detected")
        else:
            st.success("✓ No Conflict")

    # --------------------------------------------------------
    # CONFLICT
    # --------------------------------------------------------

    if has_conflict:

        st.warning(
            "The retrieved documents contain conflicting information."
        )

        if conflicts:

            st.write("**Detected conflicts:**")

            for conflict in conflicts:

                st.write(
                    f"- {conflict}"
                )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    render_sources(
        sources
    )


# ============================================================
# STEP 1 — ORGANIZATIONS
# ============================================================

def render_organizations_step():

    st.title("🏢 EnterpriseIQ")

    st.caption(
        "Evidence-grounded intelligence across enterprise documents."
    )

    st.divider()

    organizations = list_organizations()

    st.subheader("Select an organization")

    if not organizations:

        st.info(
            "No organizations yet. Create one below to get started."
        )

    for org in organizations:

        documents = get_documents(org.id)

        file_types = sorted(
            {
                document.suffix.lower().lstrip(".")
                for document in documents
            }
        )

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(f"**{org.name}**")

                if documents:
                    st.caption(
                        f"{len(documents)} document(s) • "
                        f"{', '.join(t.upper() for t in file_types)}"
                    )
                else:
                    st.caption("No documents yet.")

            with col2:

                if st.button(
                    "Select →",
                    key=f"select_{org.id}",
                    use_container_width=True,
                ):
                    select_organization(org.id)
                    st.rerun()

    st.divider()

    st.subheader("➕ Add organization")

    with st.form("new_org_form", clear_on_submit=True):

        new_name = st.text_input(
            "Organization name",
            placeholder="e.g. Acme Corp",
        )

        submitted = st.form_submit_button("Create organization")

        if submitted:

            try:
                org = create_organization(new_name)
            except ValueError as exc:
                st.error(str(exc))
            else:
                select_organization(org.id)
                st.rerun()


# ============================================================
# STEP 2 — UPLOAD
# ============================================================

def render_upload_step():

    org = get_organization(st.session_state.org_id)

    if org is None:
        go_to_orgs()
        st.rerun()
        return

    header_col, back_col = st.columns([4, 1])

    with header_col:
        st.title(f"📂 {org.name}")
        st.caption(
            "Upload the documents this organization should be searchable over."
        )

    with back_col:
        if st.button("⬅ Switch organization", use_container_width=True):
            go_to_orgs()
            st.rerun()

    st.divider()

    existing_documents = get_documents(org.id)

    if existing_documents:

        st.success(
            f"{len(existing_documents)} document(s) already indexed "
            f"for {org.name}."
        )

        if st.button(
            "Skip upload → Search documents",
            type="primary",
        ):
            go_to_query()
            st.rerun()

        st.divider()

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=[
            "pdf",
            "docx",
            "csv",
            "xlsx",
            "xls",
        ],
        accept_multiple_files=True,
    )

    if uploaded_files:

        raw_dir = organization_raw_dir(org.id)
        indexed_any = False

        for uploaded_file in uploaded_files:

            destination = raw_dir / uploaded_file.name

            with open(destination, "wb") as file:
                file.write(uploaded_file.getbuffer())

            if uploaded_file.name not in st.session_state.uploaded_names:

                st.session_state.uploaded_names.append(
                    uploaded_file.name
                )

                with st.spinner(
                    f"Indexing {uploaded_file.name}..."
                ):
                    success = index_single_document(
                        destination,
                        org.id,
                    )

                if success:
                    indexed_any = True
                    st.success(
                        f"✓ {uploaded_file.name} added to "
                        f"{org.name}'s knowledge base."
                    )

        if indexed_any:

            if st.button(
                "Continue → Search documents",
                type="primary",
                use_container_width=True,
            ):
                go_to_query()
                st.rerun()


# ============================================================
# STEP 3 — QUERY
# ============================================================

def render_query_step():

    org = get_organization(st.session_state.org_id)

    if org is None:
        go_to_orgs()
        st.rerun()
        return

    documents = get_documents(org.id)

    header_col, upload_col, back_col = st.columns([3, 1, 1])

    with header_col:
        st.title(f"🔎 Search {org.name}")
        st.caption(
            "Search across PDFs, Word documents, "
            "CSV files and Excel workbooks."
        )

    with upload_col:
        if st.button("📂 Upload more", use_container_width=True):
            go_to_upload()
            st.rerun()

    with back_col:
        if st.button("⬅ Switch org", use_container_width=True):
            go_to_orgs()
            st.rerun()

    st.divider()

    if not documents:

        st.warning(
            "No documents indexed yet for this organization."
        )

        if st.button("Go to upload"):
            go_to_upload()
            st.rerun()

        return

    left, right = st.columns(
        [2.1, 1],
        gap="large",
    )

    with left:

        question = st.text_area(
            "Your search",
            value=st.session_state.last_question,
            placeholder=(
                "Example: Who manages Aditi Sharma?"
            ),
            height=120,
        )

        if st.button(
            "Search →",
            type="primary",
            use_container_width=True,
        ):

            if not question.strip():

                st.warning(
                    "Please enter a search query."
                )

            else:

                st.session_state.last_question = (
                    question.strip()
                )

                with st.spinner(
                    "Searching documents and writing an answer..."
                ):

                    try:

                        result = run_question(
                            question.strip(),
                            org.id,
                        )

                        st.session_state.last_result = (
                            result
                        )

                    except Exception as exc:

                        st.error(
                            f"Unable to run search: {exc}"
                        )

        if st.session_state.last_result:

            st.divider()

            render_result(
                st.session_state.last_result
            )

    with right:

        st.subheader("📊 Knowledge base")

        st.metric("Documents", len(documents))

        file_types = {}

        for document in documents:
            extension = document.suffix.lower()
            file_types[extension] = file_types.get(extension, 0) + 1

        for extension, count in sorted(file_types.items()):
            st.write(f"{extension.upper()} — {count}")

        st.divider()

        if st.button(
            "🔄 Reindex all documents",
            use_container_width=True,
        ):

            with st.spinner(
                "Rebuilding knowledge base..."
            ):

                try:
                    index_documents(org.id)
                    st.session_state.graph = None
                    st.success("Reindexed.")
                except ValueError as exc:
                    st.error(str(exc))


# ============================================================
# ROUTER
# ============================================================

if not st.session_state.org_id:
    render_organizations_step()
elif st.session_state.step == "upload":
    render_upload_step()
elif st.session_state.step == "query":
    render_query_step()
else:
    render_organizations_step()


st.divider()

st.caption(
    "EnterpriseIQ • LangChain • LangGraph • Chroma • Streamlit"
)
