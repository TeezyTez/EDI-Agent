from app.models.schema import FieldSchema
from app.services.api_push_workflow import build_payload_template
from app.services.api_push_workflow import parse_api_document
import pandas as pd
import pytest


def test_build_payload_template_supports_nested_paths():
    payload = build_payload_template(
        [
            FieldSchema(field_name="order.orderNo", type="string", example="SO-1001"),
            FieldSchema(field_name="order.amount.total", type="number", example=199.5),
        ]
    )

    assert payload == {"order": {"orderNo": "SO-1001", "amount": {"total": 199.5}}}


def test_parse_api_document_supports_docx_table():
    endpoint, method, fields = parse_api_document("sample_data/target_api_doc.docx")

    assert endpoint == "/api/v1/orders/push"
    assert method == "POST"
    assert fields[0].field_name == "order.orderNo"


def test_parse_api_document_supports_text_pdf_table():
    endpoint, method, fields = parse_api_document("sample_data/target_api_doc.pdf")

    assert endpoint == "/api/v1/orders/push"
    assert method == "POST"
    assert fields[1].field_name == "order.orderDate"


def test_parse_api_document_supports_json_template_excel(tmp_path):
    path = tmp_path / "api_template.xlsx"
    df = pd.DataFrame(
        [
            ['"root": {', "", ""],
            ['"genjb_job_number": "",', "GFBL.JOB_NO", "job number"],
            ['"process_date": "09/07/25",', "today", "message date"],
            ['"genjb_company_id": 1,', "fixed", "company id"],
        ]
    )
    df.to_excel(path, index=False, header=False)

    endpoint, method, fields = parse_api_document(path)

    assert endpoint == "/"
    assert method == "POST"
    assert [field.field_name for field in fields] == ["genjb_job_number", "process_date", "genjb_company_id"]
    assert fields[-1].type == "number"


def test_parse_api_document_explains_free_form_documents_need_deepseek(monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.api_push_workflow.DEEPSEEK_API_KEY", "")
    path = tmp_path / "free_form.txt"
    path.write_text("This manifest format contains many fields but no table delimiters.", encoding="utf-8")

    with pytest.raises(ValueError, match="configure DEEPSEEK_API_KEY"):
        parse_api_document(path)
