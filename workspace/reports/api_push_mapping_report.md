# API Push Mapping Report

## Target API

- Method: `POST`
- Endpoint: `/`
- Payload template: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/target_api_payload_template.json`
- Mapping review workbook: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/mapping_review.xlsx`
- LLM: `RAG applied 1 explicit mapping hints. DeepSeek enhanced 18 low-confidence mappings with RAG context.`

## Database To API Mapping

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | documentIdentifier | 0.40 | unmatched | DeepSeek+RAG: EDI_ID is an integer identifier similar to documentIdentifier; other candidates are numeric but not identifiers.; knowledge_items=5; rule_baseline=(name=0.38, description=0.13, type=1.00, example=0.00) |
|  | versionNo | 0.40 | unmatched | name=0.24, description=0.38, type=1.00, example=0.00 |
|  | filingPartyMpciId | 0.47 | unmatched | name=0.44, description=0.27, type=1.00, example=0.00 |
|  | timestamp | 0.43 | unmatched | name=0.38, description=0.24, type=1.00, example=0.00 |
| GFBL.BL_NO | blNo | 0.90 | auto_confirmed | DeepSeek+RAG: Historical mapping and field name match for Bill of Lading number.; knowledge_items=5; rule_baseline=(RAG explicit mapping hint: blNo -> GFBL.BL_NO; rule_baseline=(name=0.62, description=0.21, type=1.00, example=0.00)) |
|  | status | 0.67 | unmatched | DeepSeek+RAG: Direct name match and highest rule score among candidates.; knowledge_items=1; rule_baseline=(name=0.71, description=0.60, type=1.00, example=0.00) |
|  | remarks | 0.46 | unmatched | name=0.59, description=0.00, type=1.00, example=0.00 |
|  | errorMessage | 0.35 | unmatched | name=0.33, description=0.00, type=1.00, example=0.00 |
|  | equipmentNumber | 0.45 | unmatched | name=0.38, description=0.31, type=1.00, example=0.00 |
| GFBL.HS_CD | hsCode | 0.90 | auto_confirmed | DeepSeek+RAG: Historical mapping explicitly maps items.hsCode to GFBL.HS_CD; field name and description match.; knowledge_items=5; rule_baseline=(name=0.59, description=0.12, type=1.00, example=0.00) |
|  | filingPartyname | 0.49 | unmatched | name=0.48, description=0.31, type=1.00, example=0.00 |
|  | filingPartyType | 0.48 | unmatched | name=0.48, description=0.26, type=1.00, example=0.00 |
|  | fileName | 0.47 | unmatched | name=0.31, description=0.54, type=1.00, example=0.00 |
|  | attachment | 0.69 | unmatched | name=0.52, description=0.64, type=1.00, example=1.00 |
|  | attachmentFileType | 0.48 | unmatched | name=0.40, description=0.41, type=1.00, example=0.00 |
|  | message | 0.46 | unmatched | name=0.53, description=0.08, type=1.00, example=0.00 |
|  | sequenceNumber | 0.42 | unmatched | DeepSeek+RAG: Field name 'SEQ' matches 'sequenceNumber' semantics; type float is numeric; required flag matches.; knowledge_items=5; rule_baseline=(name=0.34, description=0.25, type=1.00, example=0.00) |
|  | portCode | 0.55 | unmatched | DeepSeek+RAG: Best match by name and type; ITPORT_CD likely represents port code.; knowledge_items=0; rule_baseline=(name=0.55, description=0.43, type=1.00, example=0.00) |

## Need Human Review

No fields need review.

## Unmatched API Fields

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | documentIdentifier | 0.40 | unmatched | DeepSeek+RAG: EDI_ID is an integer identifier similar to documentIdentifier; other candidates are numeric but not identifiers.; knowledge_items=5; rule_baseline=(name=0.38, description=0.13, type=1.00, example=0.00) |
|  | versionNo | 0.40 | unmatched | name=0.24, description=0.38, type=1.00, example=0.00 |
|  | filingPartyMpciId | 0.47 | unmatched | name=0.44, description=0.27, type=1.00, example=0.00 |
|  | timestamp | 0.43 | unmatched | name=0.38, description=0.24, type=1.00, example=0.00 |
|  | status | 0.67 | unmatched | DeepSeek+RAG: Direct name match and highest rule score among candidates.; knowledge_items=1; rule_baseline=(name=0.71, description=0.60, type=1.00, example=0.00) |
|  | remarks | 0.46 | unmatched | name=0.59, description=0.00, type=1.00, example=0.00 |
|  | errorMessage | 0.35 | unmatched | name=0.33, description=0.00, type=1.00, example=0.00 |
|  | equipmentNumber | 0.45 | unmatched | name=0.38, description=0.31, type=1.00, example=0.00 |
|  | filingPartyname | 0.49 | unmatched | name=0.48, description=0.31, type=1.00, example=0.00 |
|  | filingPartyType | 0.48 | unmatched | name=0.48, description=0.26, type=1.00, example=0.00 |
|  | fileName | 0.47 | unmatched | name=0.31, description=0.54, type=1.00, example=0.00 |
|  | attachment | 0.69 | unmatched | name=0.52, description=0.64, type=1.00, example=1.00 |
|  | attachmentFileType | 0.48 | unmatched | name=0.40, description=0.41, type=1.00, example=0.00 |
|  | message | 0.46 | unmatched | name=0.53, description=0.08, type=1.00, example=0.00 |
|  | sequenceNumber | 0.42 | unmatched | DeepSeek+RAG: Field name 'SEQ' matches 'sequenceNumber' semantics; type float is numeric; required flag matches.; knowledge_items=5; rule_baseline=(name=0.34, description=0.25, type=1.00, example=0.00) |
|  | portCode | 0.55 | unmatched | DeepSeek+RAG: Best match by name and type; ITPORT_CD likely represents port code.; knowledge_items=0; rule_baseline=(name=0.55, description=0.43, type=1.00, example=0.00) |
