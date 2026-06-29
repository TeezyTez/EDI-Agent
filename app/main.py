from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.config import REPORT_DIR, UPLOAD_DIR, ensure_workspace
from app.services.api_push_workflow import run_api_push_mapping_workflow
from app.services.knowledge_base import add_knowledge_item, ingest_knowledge_file, list_knowledge_items
from app.services.workflow import run_mapping_workflow
from app.utils.file_loader import save_upload


app = FastAPI(title="EDI Mapping Agent", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    ensure_workspace()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/mapping/run")
async def run_mapping(
    source_fields: UploadFile = File(...),
    target_fields: UploadFile = File(...),
    source_sample: UploadFile = File(...),
    target_sample: UploadFile = File(...),
):
    source_fields_path = await save_upload(source_fields, UPLOAD_DIR / source_fields.filename)
    target_fields_path = await save_upload(target_fields, UPLOAD_DIR / target_fields.filename)
    source_sample_path = await save_upload(source_sample, UPLOAD_DIR / source_sample.filename)
    target_sample_path = await save_upload(target_sample, UPLOAD_DIR / target_sample.filename)
    result = run_mapping_workflow(source_fields_path, target_fields_path, source_sample_path, target_sample_path)
    return result.model_dump()


@app.post("/api-push-mapping/run")
async def run_api_push_mapping(
    database_doc: UploadFile = File(...),
    api_doc: UploadFile = File(...),
    knowledge_file: UploadFile | None = File(None),
    sample_files: list[UploadFile] | None = File(None),
    knowledge_files: list[UploadFile] | None = File(None),
    use_llm: bool = Form(False),
    analyze_knowledge_with_llm: bool = Form(False),
):
    database_doc_path = await save_upload(database_doc, UPLOAD_DIR / database_doc.filename)
    api_doc_path = await save_upload(api_doc, UPLOAD_DIR / api_doc.filename)
    for sample_file in sample_files or []:
        sample_path = await save_upload(sample_file, UPLOAD_DIR / sample_file.filename)
        ingest_knowledge_file(
            sample_path,
            category="business_context",
            tags=["api_push", "target_sample"],
            use_llm=analyze_knowledge_with_llm,
        )
    if knowledge_file is not None:
        knowledge_path = await save_upload(knowledge_file, UPLOAD_DIR / knowledge_file.filename)
        ingest_knowledge_file(
            knowledge_path,
            category="business_context",
            tags=["api_push"],
            use_llm=analyze_knowledge_with_llm,
        )
    for extra_knowledge_file in knowledge_files or []:
        knowledge_path = await save_upload(extra_knowledge_file, UPLOAD_DIR / extra_knowledge_file.filename)
        ingest_knowledge_file(
            knowledge_path,
            category="business_context",
            tags=["api_push"],
            use_llm=analyze_knowledge_with_llm,
        )
    result = run_api_push_mapping_workflow(database_doc_path, api_doc_path, use_llm=use_llm)
    return result.model_dump()


@app.get("/knowledge")
def list_knowledge():
    return [item.model_dump(mode="json") for item in list_knowledge_items()]


@app.post("/knowledge/text")
def create_knowledge_text(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("business_context"),
    tags: str = Form(""),
):
    item = add_knowledge_item(
        title=title,
        content=content,
        category=category,
        tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
    )
    return item.model_dump(mode="json")


@app.post("/knowledge/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    category: str = Form("business_context"),
    tags: str = Form(""),
    use_llm: bool = Form(False),
):
    file_path = await save_upload(file, UPLOAD_DIR / file.filename)
    items = ingest_knowledge_file(
        file_path,
        category=category,
        tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
        use_llm=use_llm,
    )
    return [item.model_dump(mode="json") for item in items]


@app.get("/reports/latest")
def latest_report() -> FileResponse:
    report_path = REPORT_DIR / "report.md"
    return FileResponse(report_path, media_type="text/markdown", filename="report.md")
