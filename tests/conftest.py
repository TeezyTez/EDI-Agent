import pytest


@pytest.fixture(autouse=True)
def isolate_knowledge_store(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.knowledge_base.KNOWLEDGE_STORE", tmp_path / "knowledge_items.json")
    monkeypatch.setattr("app.config.CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr("app.services.api_push_workflow.CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr("app.services.llm_mapping_enhancer.CACHE_DIR", tmp_path / "cache")
