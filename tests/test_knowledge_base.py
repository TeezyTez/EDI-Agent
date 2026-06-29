from pathlib import Path

from app.services.knowledge_base import add_knowledge_item, clear_knowledge_items, extract_file_text, ingest_knowledge_file, search_knowledge


def test_search_knowledge_returns_relevant_business_context():
    clear_knowledge_items()
    add_knowledge_item(
        title="job number mapping",
        content="genjb_job_number is the sender reference and usually maps to JOB_NO in iFreight.",
        category="historical_mapping",
        tags=["CNIIN"],
    )

    results = search_knowledge("genjb_job_number sender reference")

    assert results
    assert results[0].title == "job number mapping"


def test_ingest_knowledge_file_from_markdown(tmp_path: Path):
    clear_knowledge_items()
    path = tmp_path / "glossary.md"
    path.write_text("CTN means container number. It may map to CTN_NO.", encoding="utf-8")

    items = ingest_knowledge_file(path, category="glossary", tags=["container"])

    assert len(items) == 1
    assert search_knowledge("container CTN_NO")


def test_extract_file_text_from_markdown(tmp_path: Path):
    path = tmp_path / "notes.md"
    path.write_text("genjb_job_number maps to JOB_NO", encoding="utf-8")

    assert "JOB_NO" in extract_file_text(path)


def test_extract_file_text_from_json(tmp_path: Path):
    path = tmp_path / "sample.json"
    path.write_text('{"jobNo": "SO-1"}', encoding="utf-8")

    assert "jobNo" in extract_file_text(path)


def test_ingest_knowledge_file_with_llm_extraction(monkeypatch, tmp_path: Path):
    clear_knowledge_items()
    path = tmp_path / "notes.md"
    path.write_text("genjb_job_number maps to GFBL.JOB_NO", encoding="utf-8")

    def fake_extract(source_name, text, tags):
        return [
            {
                "title": "genjb_job_number",
                "category": "historical_mapping",
                "content": "target_field: genjb_job_number\nsource_fields: GFBL.JOB_NO",
                "tags": tags,
                "metadata": {"target_field": "genjb_job_number", "source_fields": ["GFBL.JOB_NO"]},
            }
        ]

    monkeypatch.setattr("app.services.llm_knowledge_extractor.extract_knowledge_with_deepseek", fake_extract)

    items = ingest_knowledge_file(path, category="business_context", tags=["CNIIN"], use_llm=True)

    assert items[0].category == "historical_mapping"
    assert items[0].metadata["source_fields"] == ["GFBL.JOB_NO"]


def test_ingest_knowledge_file_falls_back_when_llm_extraction_fails(monkeypatch, tmp_path: Path):
    clear_knowledge_items()
    path = tmp_path / "notes.md"
    path.write_text("Plain fallback knowledge about JOB_NO.", encoding="utf-8")

    def fake_extract(source_name, text, tags):
        raise ValueError("bad json")

    monkeypatch.setattr("app.services.llm_knowledge_extractor.extract_knowledge_with_deepseek", fake_extract)

    items = ingest_knowledge_file(path, category="business_context", tags=["CNIIN"], use_llm=True)

    assert items
    assert any("JOB_NO" in item.content for item in items)
