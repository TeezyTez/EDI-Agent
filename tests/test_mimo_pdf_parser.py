from app.services.mimo_pdf_parser import _select_request_pages


def test_select_request_pages_prefers_request_message_until_sample_section():
    pages = [
        "Contents",
        "2.3 Message Header",
        "2.4 Request Message Field Name API Tag Data Type Validation M/O/C Description",
        "BL Number blNo string AN20 M",
        "Equipment Details equipmentDetails array",
        "2.5 Sample Message",
        "2.6 Response Message",
    ]

    selected = _select_request_pages(pages, max_pages=10)

    assert selected == [2, 3, 4]


def test_select_request_pages_falls_back_to_front_pages_when_no_marker():
    selected = _select_request_pages(["cover", "table", "appendix"], max_pages=2)

    assert selected == [0, 1]
