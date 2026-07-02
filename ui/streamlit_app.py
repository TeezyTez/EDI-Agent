from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from app.config import MIMO_API_KEY, MIMO_BASE_URL, MIMO_MODEL, UPLOAD_DIR, ensure_workspace
from app.services.api_push_workflow import parse_database_document, run_api_push_mapping_workflow
from app.services.knowledge_base import add_knowledge_item, ingest_knowledge_file, list_knowledge_items, search_knowledge
from app.services.mapping_review import export_review_dataframe_excel, mappings_to_review_dataframe, persist_confirmed_mappings
from app.services.workflow import run_mapping_workflow


def _save_streamlit_upload(upload, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(upload.getbuffer())
    return path


def _ingest_knowledge_file(path: Path, category: str, tags: list[str], use_llm: bool):
    try:
        return ingest_knowledge_file(path, category=category, tags=tags, use_llm=use_llm)
    except TypeError as exc:
        if "use_llm" not in str(exc):
            raise
        st.warning("当前 Streamlit 进程还在使用旧版知识库模块，请重启 Streamlit 后再使用 DeepSeek 自动分析。已先按普通规则导入。")
        return ingest_knowledge_file(path, category=category, tags=tags)


st.set_page_config(page_title="EDI Mapping Agent", layout="wide")
st.title("EDI Mapping Agent")

ensure_workspace()

tab_edi, tab_api, tab_knowledge = st.tabs(["字段文件映射", "数据库到接口推送", "背景知识库"])

with tab_edi:
    source_fields = st.file_uploader("源系统字段说明 CSV/Excel", type=["csv", "xlsx", "xls"], key="source_fields")
    target_fields = st.file_uploader("目标系统字段说明 CSV/Excel", type=["csv", "xlsx", "xls"], key="target_fields")
    source_sample = st.file_uploader("源系统样例 JSON", type=["json"], key="source_sample")
    target_sample = st.file_uploader("目标系统样例 JSON", type=["json"], key="target_sample")

    if st.button("生成映射与报告", type="primary", disabled=not all([source_fields, target_fields, source_sample, target_sample])):
        with st.spinner("正在解析字段、生成映射、代码和测试..."):
            source_fields_path = _save_streamlit_upload(source_fields, UPLOAD_DIR / source_fields.name)
            target_fields_path = _save_streamlit_upload(target_fields, UPLOAD_DIR / target_fields.name)
            source_sample_path = _save_streamlit_upload(source_sample, UPLOAD_DIR / source_sample.name)
            target_sample_path = _save_streamlit_upload(target_sample, UPLOAD_DIR / target_sample.name)
            result = run_mapping_workflow(source_fields_path, target_fields_path, source_sample_path, target_sample_path)

        st.success("工作流执行完成")
        mapping_df = pd.DataFrame([item.model_dump() for item in result.mappings])
        st.dataframe(mapping_df, use_container_width=True)

        st.subheader("pytest 结果")
        st.code(result.pytest_output, language="text")

        report_text = Path(result.report_path).read_text(encoding="utf-8")
        st.download_button("下载 report.md", report_text, file_name="report.md", mime="text/markdown")
        st.markdown(report_text)

with tab_api:
    database_doc = st.file_uploader("我的系统数据库文档 CSV/Excel/Word/PDF", type=["csv", "xlsx", "xls", "docx", "pdf"], key="database_doc")
    api_doc = st.file_uploader("目标系统接口说明文档 CSV/Excel/Word/PDF", type=["csv", "xlsx", "xls", "docx", "pdf"], key="api_doc")
    sample_docs = st.file_uploader(
        "目标系统 sample / 示例文件，可选，可多选",
        type=["json", "txt", "md", "csv", "xlsx", "xls", "docx", "pdf"],
        accept_multiple_files=True,
        key="api_sample_docs",
    )
    knowledge_docs = st.file_uploader(
        "补充资料 / RAG 知识文件，可选，可多选",
        type=["json", "txt", "md", "csv", "xlsx", "xls", "docx", "pdf"],
        accept_multiple_files=True,
        key="api_knowledge_docs",
    )
    analyze_knowledge_with_llm = st.checkbox(
        "使用 DeepSeek 分析补充资料",
        value=False,
        help="适合格式不固定的业务资料。系统会先让大模型抽取结构化 RAG 知识，再用于接口映射。",
    )
    use_llm = st.checkbox("启用 DeepSeek 语义增强", value=False, help="需要在 .env 中配置 DEEPSEEK_API_KEY。未启用时只使用本地规则匹配。")
    llm_max_targets = st.number_input("DeepSeek 最多增强字段数", min_value=1, max_value=200, value=20, step=1)
    if api_doc is not None and api_doc.name.lower().endswith(".pdf"):
        if MIMO_API_KEY and MIMO_BASE_URL:
            st.caption(f"PDF 多模态解析：已启用 MIMO（{MIMO_MODEL}）")
        else:
            st.warning("PDF 多模态解析未启用：请在 .env 配置 MIMO_API_KEY/MIMO_BASE_URL 或 VISION_API_KEY/VISION_BASE_URL。当前会回退到文本解析，复杂 PDF 表格容易解析错。")

    if st.button("生成接口推送映射", type="primary", disabled=not all([database_doc, api_doc])):
        with st.spinner("正在生成目标接口格式和数据库字段映射文档..."):
            database_doc_path = _save_streamlit_upload(database_doc, UPLOAD_DIR / database_doc.name)
            api_doc_path = _save_streamlit_upload(api_doc, UPLOAD_DIR / api_doc.name)
            imported_count = 0
            for sample_doc in sample_docs or []:
                sample_doc_path = _save_streamlit_upload(sample_doc, UPLOAD_DIR / sample_doc.name)
                sample_items = _ingest_knowledge_file(
                    sample_doc_path,
                    category="business_context",
                    tags=["api_push", "target_sample"],
                    use_llm=analyze_knowledge_with_llm,
                )
                imported_count += len(sample_items)
            for knowledge_doc in knowledge_docs or []:
                knowledge_doc_path = _save_streamlit_upload(knowledge_doc, UPLOAD_DIR / knowledge_doc.name)
                knowledge_items = _ingest_knowledge_file(
                    knowledge_doc_path,
                    category="business_context",
                    tags=["api_push"],
                    use_llm=analyze_knowledge_with_llm,
                )
                imported_count += len(knowledge_items)
            if imported_count:
                st.info(f"已导入 sample/补充资料 {imported_count} 条")
            api_result = run_api_push_mapping_workflow(
                database_doc_path,
                api_doc_path,
                use_llm=use_llm,
                llm_max_targets=int(llm_max_targets) if use_llm else None,
            )
            st.session_state["valid_source_fields"] = {field.field_name for field in parse_database_document(database_doc_path)}

        st.success("接口推送映射生成完成")
        st.caption(f"{api_result.method} {api_result.endpoint}")
        if api_result.llm_message:
            st.info(api_result.llm_message)
        st.session_state["api_push_result"] = api_result

    api_result = st.session_state.get("api_push_result")
    if api_result:
        st.subheader("映射审查")
        review_df = mappings_to_review_dataframe(api_result.mappings)
        edited_review_df = st.data_editor(
            review_df,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "review_decision": st.column_config.SelectboxColumn(
                    "review_decision",
                    options=["confirm", "modify", "reject", "unmatched"],
                    required=True,
                ),
                "confirmed_source_field": st.column_config.TextColumn("confirmed_source_field"),
                "review_note": st.column_config.TextColumn("review_note"),
            },
            disabled=["target_field", "suggested_source_field", "confidence", "status", "rule_type", "reason"],
            key="mapping_review_editor",
        )

        col_save, col_export = st.columns(2)
        with col_save:
            if st.button("保存人工确认到 RAG", type="primary"):
                saved = persist_confirmed_mappings(
                    edited_review_df,
                    tags=["human_review", "api_push"],
                    valid_source_fields=st.session_state.get("valid_source_fields"),
                )
                review_path = export_review_dataframe_excel(edited_review_df)
                st.success(f"已沉淀 {saved} 条人工确认映射到知识库")
                st.caption(f"审查 Excel 已更新：{review_path}")
        with col_export:
            review_path = export_review_dataframe_excel(edited_review_df)
            review_bytes = Path(review_path).read_bytes()
            st.download_button(
                "下载 mapping_review.xlsx",
                review_bytes,
                file_name="mapping_review.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        payload_text = Path(api_result.payload_template_path).read_text(encoding="utf-8")
        report_text = Path(api_result.mapping_report_path).read_text(encoding="utf-8")
        st.subheader("目标系统接口格式")
        st.code(payload_text, language="json")
        st.download_button("下载目标接口 payload 模板", payload_text, file_name="target_api_payload_template.json", mime="application/json")
        st.download_button("下载映射文档", report_text, file_name="api_push_mapping_report.md", mime="text/markdown")
        if api_result.mapping_review_path:
            st.caption(f"映射审查文件：{api_result.mapping_review_path}")
        st.markdown(report_text)

with tab_knowledge:
    st.subheader("补充背景知识")
    category = st.selectbox(
        "知识类型",
        ["business_context", "field_alias", "historical_mapping", "glossary", "enum_mapping", "fixed_value_rule"],
        index=0,
    )
    tags = st.text_input("标签，逗号分隔", placeholder="CNIIN, OLS, iFreight")

    st.markdown("#### 手工录入")
    title = st.text_input("标题", placeholder="genjb_job_number 对应业务号")
    content = st.text_area(
        "内容",
        placeholder="例如：genjb_job_number 是发送方唯一业务参考号，iFreight 中通常对应 JOB_NO 或业务号字段。",
        height=140,
    )
    if st.button("保存知识", disabled=not content.strip()):
        item = add_knowledge_item(
            title=title or content[:30],
            content=content,
            category=category,
            tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
        )
        st.success(f"已保存：{item.title}")

    st.markdown("#### 上传知识文件")
    knowledge_file = st.file_uploader("支持 txt/md/csv/xlsx/xls/docx/pdf", type=["txt", "md", "csv", "xlsx", "xls", "docx", "pdf"])
    use_llm_for_knowledge = st.checkbox(
        "使用 DeepSeek 自动分析这个知识文件",
        value=False,
        help="从任意格式资料中抽取字段映射、固定值、枚举、转换规则和业务术语。",
        key="knowledge_use_llm",
    )
    if st.button("导入知识文件", disabled=knowledge_file is None):
        knowledge_path = _save_streamlit_upload(knowledge_file, UPLOAD_DIR / knowledge_file.name)
        items = _ingest_knowledge_file(
            knowledge_path,
            category=category,
            tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
            use_llm=use_llm_for_knowledge,
        )
        st.success(f"已导入 {len(items)} 条知识")

    st.markdown("#### 检索预览")
    query = st.text_input("测试检索", placeholder="genjb_job_number / container number / postal code")
    if query:
        results = search_knowledge(query, limit=5)
        st.caption(f"命中 {len(results)} 条")
        for item in results:
            with st.expander(f"{item.category} | {item.title}"):
                st.write(item.content)
                if item.tags:
                    st.caption(", ".join(item.tags))

    st.markdown("#### 当前知识")
    items = list_knowledge_items()
    st.caption(f"共 {len(items)} 条")
    if items:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "title": item.title,
                        "category": item.category,
                        "tags": ", ".join(item.tags),
                        "created_at": item.created_at,
                        "content": item.content[:120],
                    }
                    for item in items[:200]
                ]
            ),
            use_container_width=True,
        )
