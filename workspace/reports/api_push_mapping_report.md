# API Push Mapping Report

## Target API

- Method: `POST`
- Endpoint: `/`
- Payload template: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/target_api_payload_template.json`
- Mapping review workbook: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/mapping_review.xlsx`
- Mapping diagnostics: `D:/Workspace/EDI Agent/edi-agent/workspace/reports/mapping_diagnostics.json`
- LLM: `RAG applied 10 explicit mapping hints. DeepSeek decided 20/20 mappings with RAG context, 20 candidates per target, and 3 worker(s).`

## Database To API Mapping

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | Decimal_point | 0.80 | need_review | DeepSeek+RAG: Target field description states the decimal marker must be a comma; no direct source field exists; fixed value rule from sample indicates comma.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.60, name_tokens=0.25, description=0.10, type=1.00, example=1.00) |
|  | Numeric_seperator | 1.00 | auto_confirmed | DeepSeek+RAG: Fixed value indicating decimal separator is full stop.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.29, name_tokens=0.67, description=0.31, type=1.00, example=1.00) |
|  | genjb_comment | 0.10 | unmatched | DeepSeek+RAG: No matching source column found for free-text comment field.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.00, description=0.28, type=1.00, example=1.00) |
| GFBK.JOB_NO | genjb_job_number | 0.80 | need_review | DeepSeek+RAG: Field name and description match job number; highest rule score among candidates.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.59, name_tokens=0.87, description=0.23, type=1.00, example=1.00) |
|  | genjb_qjob_job_code | 1.00 | auto_confirmed | DeepSeek+RAG: Field description is 'CNIIN' and business knowledge confirms it is always 'CNIIN' (fixed value rule).; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.38, description=0.33, type=1.00, example=1.00) |
|  | genjb_description | 0.80 | need_review | DeepSeek+RAG: Sample data shows fixed value 'OLS CNI Integration' for genjb_description; no database column directly maps; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.50, name_tokens=0.00, description=0.52, type=1.00, example=1.00) |
|  | genjb_company_id | 0.95 | auto_confirmed | DeepSeek+RAG: Retrieved business knowledge explicitly states company ID is always 1 for this integration.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.50, name_tokens=0.00, description=0.21, type=1.00, example=1.00) |
|  | genjb_qsts_code | 0.95 | auto_confirmed | DeepSeek+RAG: Based on business knowledge, genjb_qsts_code is always 'REQ' for new requests. Sample data confirms fixed value.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.52, name_tokens=0.25, description=0.44, type=1.00, example=1.00) |
|  | genjb_qstsx_definition | 0.10 | unmatched | DeepSeek+RAG: No credible source field found for this description field; it likely maps to a status code (e.g., genjb_qsts_code) which is not present in candidate database fields.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.46, name_tokens=0.00, description=0.36, type=1.00, example=1.00) |
| GFSETNO.CREATE_DATE | process_date | 0.85 | need_review | DeepSeek+RAG: GFSETNO.CREATE_DATE represents creation date, matching process_date semantics; business knowledge sample confirms process_date format.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.44, name_tokens=0.21, description=0.58, type=0.00, example=1.00) |
|  | CNI_docs_to_print | 0.10 | unmatched | DeepSeek+RAG: No direct database column matches. Target is a complex string of document codes and printer paths; likely constructed from multiple sources not in candidate list or from configuration.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.50, name_tokens=0.17, description=0.03, type=1.00, example=1.00) |
| GFBK.ORD_NM | genjbde_nad_name_1 | 0.70 | need_review | DeepSeek+RAG: GFBK.ORD_NM (booking party name) is the most credible candidate for sender name, as the booking party often represents the sender.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.50, description=0.36, type=1.00, example=1.00) |
| GFBK.ORD_NM | genjbde_nad_name_2 | 0.70 | need_review | DeepSeek+RAG: Highest scoring party name field that could represent sender name 2.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.50, description=0.36, type=1.00, example=1.00) |
| GFBL.SHPR_ADDR | genjbde_nad_street_1 | 0.90 | auto_confirmed | DeepSeek+RAG: Direct mapping based on historical mapping and semantic match for sender address.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.38, name_tokens=0.00, description=0.35, type=1.00, example=1.00) |
|  | genjbde_nad_street_2 | 0.60 | unmatched | DeepSeek+RAG: Target field is street2 of sender address. Historical mapping shows sender address from GFBL.SHPR_ADDR. No explicit street2 field; likely part of address field requiring split.; mapping_type=split; knowledge_items=5; candidates=20; rule_baseline=(name=0.38, name_tokens=0.00, description=0.33, type=1.00, example=1.00) |
|  | genjbde_nad_postal_code | 0.10 | unmatched | DeepSeek+RAG: No candidate database field semantically matches 'postal code'; all candidates are code fields (e.g., SA_CODE, EDI_CODE).; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.57, name_tokens=0.44, description=0.44, type=1.00, example=1.00) |
| BSCODE.LOCATION | genjbde_nad_location | 0.76 | need_review | DeepSeek+RAG: Best candidate based on field name and semantic similarity; BSCODE.LOCATION has highest score among location-related fields.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.69, name_tokens=0.12, description=0.53, type=1.00, example=1.00) |
| BSCS.CNTY_CD | genjbde_nad_country_iso_code | 0.80 | need_review | DeepSeek+RAG: Direct mapping to country code field.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.62, name_tokens=0.42, description=0.35, type=1.00, example=1.00) |
|  | qnbr_number_code | 0.95 | auto_confirmed | DeepSeek+RAG: Business knowledge indicates qnbr_number_code is a fixed value 'OLS' used as address code identifier.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(RAG fixed value hint: qnbr_number_code = OLS; knowledge_target=(qnbr_number_code); rule_baseline=(name=0.43, name_tokens=0.80, description=0.52, type=1.00, example=1.00)) |
|  | qnbrx_definition | 0.10 | unmatched | DeepSeek+RAG: No matching database field; likely a fixed definition value from OLS system.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.22, name_tokens=0.67, description=0.47, type=1.00, example=1.00) |
| GFBK.RAR_NO | nbr_value | 0.71 | need_review | name=0.30, name_tokens=0.73, description=0.32, type=1.00, example=1.00 |
|  | cni_description | 0.59 | unmatched | name=0.44, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qtp0_type_0_code | 0.67 | unmatched | name=0.34, name_tokens=0.67, description=0.27, type=1.00, example=1.00 |
|  | qtp0x_definition | 0.59 | unmatched | name=0.20, name_tokens=0.50, description=0.27, type=1.00, example=1.00 |
|  | qtp1_type_1_code | 0.67 | unmatched | name=0.34, name_tokens=0.67, description=0.27, type=1.00, example=1.00 |
|  | qtp1x_definition | 0.60 | unmatched | name=0.20, name_tokens=0.50, description=0.31, type=1.00, example=1.00 |
|  | qtp2_type_2_code | 0.66 | unmatched | name=0.34, name_tokens=0.67, description=0.23, type=1.00, example=1.00 |
|  | qtp2x_definition | 0.59 | unmatched | name=0.20, name_tokens=0.50, description=0.25, type=1.00, example=1.00 |
|  | qtp3_type_3_code | 0.65 | unmatched | name=0.34, name_tokens=0.67, description=0.22, type=1.00, example=1.00 |
|  | qtp3x_definition | 0.60 | unmatched | name=0.34, name_tokens=0.00, description=0.59, type=1.00, example=1.00 |
|  | qtp4_type_4_code | 0.66 | unmatched | name=0.34, name_tokens=0.67, description=0.26, type=1.00, example=1.00 |
|  | qtp4x_definition | 0.57 | unmatched | name=0.45, name_tokens=0.00, description=0.26, type=1.00, example=1.00 |
|  | qtp5_type_5_code | 0.68 | unmatched | name=0.34, name_tokens=0.67, description=0.32, type=1.00, example=1.00 |
|  | qtp5x_definition | 0.62 | unmatched | name=0.20, name_tokens=0.50, description=0.40, type=1.00, example=1.00 |
|  | cni_traffic_code | 0.61 | unmatched | name=0.62, name_tokens=0.50, description=0.14, type=1.00, example=1.00 |
|  | cni_traffic_definition | 0.63 | unmatched | name=0.52, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | cni_status_code | 0.64 | unmatched | name=0.69, name_tokens=0.50, description=0.12, type=1.00, example=1.00 |
|  | cni_file_manager | 0.61 | unmatched | name=0.69, name_tokens=0.11, description=0.02, type=1.00, example=1.00 |
| BSCS.ACI_CODE | cni_activity_code | 0.71 | need_review | name=0.67, name_tokens=0.50, description=0.44, type=1.00, example=1.00 |
| GFBK.CARRIER_CONTRACT_NO | cnict_container_number | 0.82 | need_review | name=0.43, name_tokens=0.81, description=0.61, type=1.00, example=1.00 |
|  | qcntst_code | 0.66 | unmatched | name=0.72, name_tokens=0.57, description=0.16, type=1.00, example=1.00 |
|  | qcntstx_definition | 0.61 | unmatched | name=0.47, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qcnts_container_size_code | 0.65 | unmatched | name=0.65, name_tokens=0.31, description=0.23, type=1.00, example=1.00 |
|  | qcntsx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | qcntt_container_type_code | 0.68 | unmatched | name=0.56, name_tokens=0.65, description=0.34, type=1.00, example=1.00 |
|  | qcnttx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | qcnth_container_height_code | 0.60 | unmatched | name=0.29, name_tokens=0.53, description=0.26, type=1.00, example=1.00 |
|  | qcnthx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.49, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.95 | auto_confirmed | RAG fixed value hint: qref_custom_reference = PARTY; knowledge_target=(qref_custom_reference); rule_baseline=(name=0.59, name_tokens=0.22, description=0.25, type=1.00, example=1.00) |
|  | qrefx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | cnire_value | 0.56 | unmatched | name=0.34, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordl3_line_number | 0.53 | unmatched | name=0.19, name_tokens=0.67, description=0.50, type=0.00, example=1.00 |
| GFBK.RAR_NO | wmsar_article_number | 0.77 | need_review | name=0.26, name_tokens=0.67, description=0.67, type=1.00, example=1.00 |
|  | wmsordst_number_order | 0.51 | unmatched | name=0.33, name_tokens=0.33, description=0.26, type=1.00, example=1.00 |
|  | wmsordst_order_qmus_measure_code | 0.61 | unmatched | name=0.51, name_tokens=0.36, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_wmswc_warehouse_complex_code | 0.51 | unmatched | name=0.33, name_tokens=0.36, description=0.19, type=1.00, example=1.00 |
|  | wmsordst_1_wmswcx_definition | 0.54 | unmatched | name=0.33, name_tokens=0.00, description=0.35, type=1.00, example=1.00 |
|  | wmsordst_1_wmswa_warehouse_code | 0.56 | unmatched | name=0.52, name_tokens=0.36, description=0.11, type=1.00, example=1.00 |
|  | wmsordst_1_wmswax_description | 0.58 | unmatched | name=0.38, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_wmswu_warehouse_unit_code | 0.54 | unmatched | name=0.40, name_tokens=0.45, description=0.14, type=1.00, example=1.00 |
|  | wmsordst_1_wmswux_definition | 0.52 | unmatched | name=0.43, name_tokens=0.00, description=0.09, type=1.00, example=1.00 |
|  | wmsordst_1_wmswl_warehouse_location_code | 0.59 | unmatched | name=0.47, name_tokens=0.50, description=0.25, type=1.00, example=1.00 |
|  | wmsordst_1_wmswlx_description | 0.60 | unmatched | name=0.41, name_tokens=0.00, description=0.46, type=1.00, example=1.00 |
| GFBK.LOT_NO | wmsordst_1_lot_number_1 | 0.82 | need_review | name=0.35, name_tokens=0.75, description=0.75, type=1.00, example=1.00 |
| GFBK.RAR_NO | wmsordst_1_serial_number_1 | 0.73 | need_review | name=0.16, name_tokens=0.62, description=0.62, type=1.00, example=1.00 |
|  | wmsordst_1_qcus_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_qcus_code = T1; knowledge_target=(wmsordst_1_qcus_code); rule_baseline=(name=0.53, name_tokens=0.44, description=0.40, type=1.00, example=1.00) |
|  | wmsordst_1_qcusx_definition | 0.59 | unmatched | name=0.45, name_tokens=0.00, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_qreg_regime_code | 0.62 | unmatched | name=0.52, name_tokens=0.36, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_qregx_definition | 0.61 | unmatched | name=0.42, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_storage_option1_code = CEELNR; knowledge_target=(wmsordst_1_storage_option1_code); rule_baseline=(name=0.47, name_tokens=0.40, description=0.33, type=1.00, example=1.00) |
|  | wmsordst_1_storage_option1_definition | 0.57 | unmatched | name=0.33, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_storage_option2_code = CONTAINERNR; knowledge_target=(wmsordst_1_storage_option2_code); rule_baseline=(name=0.47, name_tokens=0.40, description=0.31, type=1.00, example=1.00) |
|  | wmsordst_1_storage_option2_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_storage_option3_code = PRODUCTDESCR; knowledge_target=(wmsordst_1_storage_option3_code); rule_baseline=(name=0.47, name_tokens=0.40, description=0.31, type=1.00, example=1.00) |
|  | wmsordst_1_storage_option3_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_code | 0.59 | unmatched | name=0.47, name_tokens=0.40, description=0.31, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_storage_option5_code = CUSTDC; knowledge_target=(wmsordst_1_storage_option5_code); rule_baseline=(name=0.47, name_tokens=0.40, description=0.31, type=1.00, example=1.00) |
|  | wmsordst_1_storage_option5_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_qsts_code | 0.95 | auto_confirmed | RAG fixed value hint: wmsordst_1_qsts_code = FREE; knowledge_target=(wmsordst_1_qsts_code); rule_baseline=(name=0.57, name_tokens=0.44, description=0.11, type=1.00, example=1.00) |
|  | wmsordst_1_qstsx_definition | 0.61 | unmatched | name=0.47, name_tokens=0.00, description=0.40, type=1.00, example=1.00 |
|  | wmsordto_Tot_gross_weight | 0.55 | unmatched | name=0.32, name_tokens=0.38, description=0.31, type=1.00, example=1.00 |
|  | wmsordto_Tot_Net_weight | 0.63 | unmatched | name=0.51, name_tokens=0.50, description=0.40, type=1.00, example=1.00 |
|  | wmsordto_Tot_Volume | 0.51 | unmatched | name=0.34, name_tokens=0.15, description=0.23, type=1.00, example=1.00 |
|  | wmsordd_weight_qmus_measure_code | 0.59 | unmatched | name=0.51, name_tokens=0.27, description=0.25, type=1.00, example=1.00 |
|  | wmsordd_volume_qmus_measure_code | 0.59 | unmatched | name=0.51, name_tokens=0.27, description=0.25, type=1.00, example=1.00 |
|  | wmsordd_volume | 0.52 | unmatched | name=0.38, name_tokens=0.00, description=0.19, type=1.00, example=1.00 |
|  | wmsordd_length | 0.49 | unmatched | name=0.27, name_tokens=0.00, description=0.26, type=1.00, example=1.00 |
|  | wmsordd_width | 0.53 | unmatched | name=0.28, name_tokens=0.43, description=0.15, type=1.00, example=1.00 |
|  | wmsordd_height | 0.47 | unmatched | name=0.34, name_tokens=0.00, description=0.05, type=1.00, example=1.00 |
|  | wmsardc_definition | 0.64 | unmatched | name=0.54, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qftx_free_text_code | 0.67 | unmatched | name=0.55, name_tokens=0.19, description=0.52, type=1.00, example=1.00 |
|  | qftxx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.95 | auto_confirmed | RAG fixed value hint: qref_custom_reference = PARTY; knowledge_target=(qref_custom_reference); rule_baseline=(name=0.51, name_tokens=0.17, description=0.49, type=1.00, example=1.00) |
|  | qrefx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | cnire_value | 0.56 | unmatched | name=0.36, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | cnitmm_voyage_number | 0.61 | unmatched | name=0.19, name_tokens=0.57, description=0.21, type=1.00, example=1.00 |
|  | cnitmm_vessel_name | 0.67 | unmatched | name=0.61, name_tokens=0.69, description=0.25, type=1.00, example=1.00 |
|  | qloc_location_qual | 0.62 | unmatched | name=0.61, name_tokens=0.06, description=0.19, type=1.00, example=1.00 |
|  | cnipl_country_country_code | 0.62 | unmatched | name=0.60, name_tokens=0.36, description=0.20, type=1.00, example=1.00 |
|  | cnipl_locode_location_code | 0.68 | unmatched | name=0.37, name_tokens=0.77, description=0.15, type=1.00, example=1.00 |
|  | qdoc_code | 0.95 | auto_confirmed | RAG fixed value hint: qdoc_code = B/L; knowledge_target=(qdoc_code); rule_baseline=(name=0.60, name_tokens=0.21, description=0.33, type=1.00, example=1.00) |
|  | cnido_document_number | 0.68 | unmatched | name=0.19, name_tokens=0.67, description=0.32, type=1.00, example=1.00 |
|  | cnido_place_of_issue | 0.59 | unmatched | name=0.50, name_tokens=0.05, description=0.26, type=1.00, example=1.00 |
|  | cnido_date_of_issue | 0.43 | unmatched | name=0.57, name_tokens=0.05, description=0.30, type=0.00, example=1.00 |

## Need Human Review

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | Decimal_point | 0.80 | need_review | DeepSeek+RAG: Target field description states the decimal marker must be a comma; no direct source field exists; fixed value rule from sample indicates comma.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.60, name_tokens=0.25, description=0.10, type=1.00, example=1.00) |
| GFBK.JOB_NO | genjb_job_number | 0.80 | need_review | DeepSeek+RAG: Field name and description match job number; highest rule score among candidates.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.59, name_tokens=0.87, description=0.23, type=1.00, example=1.00) |
|  | genjb_description | 0.80 | need_review | DeepSeek+RAG: Sample data shows fixed value 'OLS CNI Integration' for genjb_description; no database column directly maps; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.50, name_tokens=0.00, description=0.52, type=1.00, example=1.00) |
| GFSETNO.CREATE_DATE | process_date | 0.85 | need_review | DeepSeek+RAG: GFSETNO.CREATE_DATE represents creation date, matching process_date semantics; business knowledge sample confirms process_date format.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.44, name_tokens=0.21, description=0.58, type=0.00, example=1.00) |
| GFBK.ORD_NM | genjbde_nad_name_1 | 0.70 | need_review | DeepSeek+RAG: GFBK.ORD_NM (booking party name) is the most credible candidate for sender name, as the booking party often represents the sender.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.50, description=0.36, type=1.00, example=1.00) |
| GFBK.ORD_NM | genjbde_nad_name_2 | 0.70 | need_review | DeepSeek+RAG: Highest scoring party name field that could represent sender name 2.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.50, description=0.36, type=1.00, example=1.00) |
| BSCODE.LOCATION | genjbde_nad_location | 0.76 | need_review | DeepSeek+RAG: Best candidate based on field name and semantic similarity; BSCODE.LOCATION has highest score among location-related fields.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.69, name_tokens=0.12, description=0.53, type=1.00, example=1.00) |
| BSCS.CNTY_CD | genjbde_nad_country_iso_code | 0.80 | need_review | DeepSeek+RAG: Direct mapping to country code field.; mapping_type=direct; knowledge_items=5; candidates=20; rule_baseline=(name=0.62, name_tokens=0.42, description=0.35, type=1.00, example=1.00) |
| GFBK.RAR_NO | nbr_value | 0.71 | need_review | name=0.30, name_tokens=0.73, description=0.32, type=1.00, example=1.00 |
| BSCS.ACI_CODE | cni_activity_code | 0.71 | need_review | name=0.67, name_tokens=0.50, description=0.44, type=1.00, example=1.00 |
| GFBK.CARRIER_CONTRACT_NO | cnict_container_number | 0.82 | need_review | name=0.43, name_tokens=0.81, description=0.61, type=1.00, example=1.00 |
| GFBK.RAR_NO | wmsar_article_number | 0.77 | need_review | name=0.26, name_tokens=0.67, description=0.67, type=1.00, example=1.00 |
| GFBK.LOT_NO | wmsordst_1_lot_number_1 | 0.82 | need_review | name=0.35, name_tokens=0.75, description=0.75, type=1.00, example=1.00 |
| GFBK.RAR_NO | wmsordst_1_serial_number_1 | 0.73 | need_review | name=0.16, name_tokens=0.62, description=0.62, type=1.00, example=1.00 |

## Unmatched API Fields

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | genjb_comment | 0.10 | unmatched | DeepSeek+RAG: No matching source column found for free-text comment field.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.53, name_tokens=0.00, description=0.28, type=1.00, example=1.00) |
|  | genjb_qstsx_definition | 0.10 | unmatched | DeepSeek+RAG: No credible source field found for this description field; it likely maps to a status code (e.g., genjb_qsts_code) which is not present in candidate database fields.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.46, name_tokens=0.00, description=0.36, type=1.00, example=1.00) |
|  | CNI_docs_to_print | 0.10 | unmatched | DeepSeek+RAG: No direct database column matches. Target is a complex string of document codes and printer paths; likely constructed from multiple sources not in candidate list or from configuration.; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.50, name_tokens=0.17, description=0.03, type=1.00, example=1.00) |
|  | genjbde_nad_street_2 | 0.60 | unmatched | DeepSeek+RAG: Target field is street2 of sender address. Historical mapping shows sender address from GFBL.SHPR_ADDR. No explicit street2 field; likely part of address field requiring split.; mapping_type=split; knowledge_items=5; candidates=20; rule_baseline=(name=0.38, name_tokens=0.00, description=0.33, type=1.00, example=1.00) |
|  | genjbde_nad_postal_code | 0.10 | unmatched | DeepSeek+RAG: No candidate database field semantically matches 'postal code'; all candidates are code fields (e.g., SA_CODE, EDI_CODE).; mapping_type=unmatched; knowledge_items=5; candidates=20; rule_baseline=(name=0.57, name_tokens=0.44, description=0.44, type=1.00, example=1.00) |
|  | qnbrx_definition | 0.10 | unmatched | DeepSeek+RAG: No matching database field; likely a fixed definition value from OLS system.; mapping_type=fixed_value; knowledge_items=5; candidates=20; rule_baseline=(name=0.22, name_tokens=0.67, description=0.47, type=1.00, example=1.00) |
|  | cni_description | 0.59 | unmatched | name=0.44, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qtp0_type_0_code | 0.67 | unmatched | name=0.34, name_tokens=0.67, description=0.27, type=1.00, example=1.00 |
|  | qtp0x_definition | 0.59 | unmatched | name=0.20, name_tokens=0.50, description=0.27, type=1.00, example=1.00 |
|  | qtp1_type_1_code | 0.67 | unmatched | name=0.34, name_tokens=0.67, description=0.27, type=1.00, example=1.00 |
|  | qtp1x_definition | 0.60 | unmatched | name=0.20, name_tokens=0.50, description=0.31, type=1.00, example=1.00 |
|  | qtp2_type_2_code | 0.66 | unmatched | name=0.34, name_tokens=0.67, description=0.23, type=1.00, example=1.00 |
|  | qtp2x_definition | 0.59 | unmatched | name=0.20, name_tokens=0.50, description=0.25, type=1.00, example=1.00 |
|  | qtp3_type_3_code | 0.65 | unmatched | name=0.34, name_tokens=0.67, description=0.22, type=1.00, example=1.00 |
|  | qtp3x_definition | 0.60 | unmatched | name=0.34, name_tokens=0.00, description=0.59, type=1.00, example=1.00 |
|  | qtp4_type_4_code | 0.66 | unmatched | name=0.34, name_tokens=0.67, description=0.26, type=1.00, example=1.00 |
|  | qtp4x_definition | 0.57 | unmatched | name=0.45, name_tokens=0.00, description=0.26, type=1.00, example=1.00 |
|  | qtp5_type_5_code | 0.68 | unmatched | name=0.34, name_tokens=0.67, description=0.32, type=1.00, example=1.00 |
|  | qtp5x_definition | 0.62 | unmatched | name=0.20, name_tokens=0.50, description=0.40, type=1.00, example=1.00 |
|  | cni_traffic_code | 0.61 | unmatched | name=0.62, name_tokens=0.50, description=0.14, type=1.00, example=1.00 |
|  | cni_traffic_definition | 0.63 | unmatched | name=0.52, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | cni_status_code | 0.64 | unmatched | name=0.69, name_tokens=0.50, description=0.12, type=1.00, example=1.00 |
|  | cni_file_manager | 0.61 | unmatched | name=0.69, name_tokens=0.11, description=0.02, type=1.00, example=1.00 |
|  | qcntst_code | 0.66 | unmatched | name=0.72, name_tokens=0.57, description=0.16, type=1.00, example=1.00 |
|  | qcntstx_definition | 0.61 | unmatched | name=0.47, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qcnts_container_size_code | 0.65 | unmatched | name=0.65, name_tokens=0.31, description=0.23, type=1.00, example=1.00 |
|  | qcntsx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | qcntt_container_type_code | 0.68 | unmatched | name=0.56, name_tokens=0.65, description=0.34, type=1.00, example=1.00 |
|  | qcnttx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | qcnth_container_height_code | 0.60 | unmatched | name=0.29, name_tokens=0.53, description=0.26, type=1.00, example=1.00 |
|  | qcnthx_definition | 0.63 | unmatched | name=0.47, name_tokens=0.00, description=0.49, type=1.00, example=1.00 |
|  | qrefx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | cnire_value | 0.56 | unmatched | name=0.34, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordl3_line_number | 0.53 | unmatched | name=0.19, name_tokens=0.67, description=0.50, type=0.00, example=1.00 |
|  | wmsordst_number_order | 0.51 | unmatched | name=0.33, name_tokens=0.33, description=0.26, type=1.00, example=1.00 |
|  | wmsordst_order_qmus_measure_code | 0.61 | unmatched | name=0.51, name_tokens=0.36, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_wmswc_warehouse_complex_code | 0.51 | unmatched | name=0.33, name_tokens=0.36, description=0.19, type=1.00, example=1.00 |
|  | wmsordst_1_wmswcx_definition | 0.54 | unmatched | name=0.33, name_tokens=0.00, description=0.35, type=1.00, example=1.00 |
|  | wmsordst_1_wmswa_warehouse_code | 0.56 | unmatched | name=0.52, name_tokens=0.36, description=0.11, type=1.00, example=1.00 |
|  | wmsordst_1_wmswax_description | 0.58 | unmatched | name=0.38, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_wmswu_warehouse_unit_code | 0.54 | unmatched | name=0.40, name_tokens=0.45, description=0.14, type=1.00, example=1.00 |
|  | wmsordst_1_wmswux_definition | 0.52 | unmatched | name=0.43, name_tokens=0.00, description=0.09, type=1.00, example=1.00 |
|  | wmsordst_1_wmswl_warehouse_location_code | 0.59 | unmatched | name=0.47, name_tokens=0.50, description=0.25, type=1.00, example=1.00 |
|  | wmsordst_1_wmswlx_description | 0.60 | unmatched | name=0.41, name_tokens=0.00, description=0.46, type=1.00, example=1.00 |
|  | wmsordst_1_qcusx_definition | 0.59 | unmatched | name=0.45, name_tokens=0.00, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_qreg_regime_code | 0.62 | unmatched | name=0.52, name_tokens=0.36, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_qregx_definition | 0.61 | unmatched | name=0.42, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_definition | 0.57 | unmatched | name=0.33, name_tokens=0.00, description=0.47, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_code | 0.59 | unmatched | name=0.47, name_tokens=0.40, description=0.31, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_definition | 0.56 | unmatched | name=0.33, name_tokens=0.00, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_value | 0.60 | unmatched | name=0.43, name_tokens=0.00, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_qstsx_definition | 0.61 | unmatched | name=0.47, name_tokens=0.00, description=0.40, type=1.00, example=1.00 |
|  | wmsordto_Tot_gross_weight | 0.55 | unmatched | name=0.32, name_tokens=0.38, description=0.31, type=1.00, example=1.00 |
|  | wmsordto_Tot_Net_weight | 0.63 | unmatched | name=0.51, name_tokens=0.50, description=0.40, type=1.00, example=1.00 |
|  | wmsordto_Tot_Volume | 0.51 | unmatched | name=0.34, name_tokens=0.15, description=0.23, type=1.00, example=1.00 |
|  | wmsordd_weight_qmus_measure_code | 0.59 | unmatched | name=0.51, name_tokens=0.27, description=0.25, type=1.00, example=1.00 |
|  | wmsordd_volume_qmus_measure_code | 0.59 | unmatched | name=0.51, name_tokens=0.27, description=0.25, type=1.00, example=1.00 |
|  | wmsordd_volume | 0.52 | unmatched | name=0.38, name_tokens=0.00, description=0.19, type=1.00, example=1.00 |
|  | wmsordd_length | 0.49 | unmatched | name=0.27, name_tokens=0.00, description=0.26, type=1.00, example=1.00 |
|  | wmsordd_width | 0.53 | unmatched | name=0.28, name_tokens=0.43, description=0.15, type=1.00, example=1.00 |
|  | wmsordd_height | 0.47 | unmatched | name=0.34, name_tokens=0.00, description=0.05, type=1.00, example=1.00 |
|  | wmsardc_definition | 0.64 | unmatched | name=0.54, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | qftx_free_text_code | 0.67 | unmatched | name=0.55, name_tokens=0.19, description=0.52, type=1.00, example=1.00 |
|  | qftxx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | qrefx_definition | 0.66 | unmatched | name=0.52, name_tokens=0.00, description=0.50, type=1.00, example=1.00 |
|  | cnire_value | 0.56 | unmatched | name=0.36, name_tokens=0.00, description=0.38, type=1.00, example=1.00 |
|  | cnitmm_voyage_number | 0.61 | unmatched | name=0.19, name_tokens=0.57, description=0.21, type=1.00, example=1.00 |
|  | cnitmm_vessel_name | 0.67 | unmatched | name=0.61, name_tokens=0.69, description=0.25, type=1.00, example=1.00 |
|  | qloc_location_qual | 0.62 | unmatched | name=0.61, name_tokens=0.06, description=0.19, type=1.00, example=1.00 |
|  | cnipl_country_country_code | 0.62 | unmatched | name=0.60, name_tokens=0.36, description=0.20, type=1.00, example=1.00 |
|  | cnipl_locode_location_code | 0.68 | unmatched | name=0.37, name_tokens=0.77, description=0.15, type=1.00, example=1.00 |
|  | cnido_document_number | 0.68 | unmatched | name=0.19, name_tokens=0.67, description=0.32, type=1.00, example=1.00 |
|  | cnido_place_of_issue | 0.59 | unmatched | name=0.50, name_tokens=0.05, description=0.26, type=1.00, example=1.00 |
|  | cnido_date_of_issue | 0.43 | unmatched | name=0.57, name_tokens=0.05, description=0.30, type=0.00, example=1.00 |
