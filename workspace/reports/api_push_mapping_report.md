# API Push Mapping Report

## Target API

- Method: `POST`
- Endpoint: `/`
- Payload template: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/target_api_payload_template.json`
- Mapping review workbook: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/mapping_review.xlsx`
- LLM: `RAG applied 0 explicit mapping hints. DeepSeek enhanced 20 low-confidence mappings with RAG context.`

## Database To API Mapping

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | Decimal_point | 0.60 | unmatched | DeepSeek+RAG: Field name 'LOCAL_DECIMAL_POINT' matches target 'Decimal_point' semantics; description '本幣小數位' (local currency decimal places) aligns with decimal marker usage.; knowledge_items=1; rule_baseline=(name=0.50, description=0.31, type=1.00, example=1.00) |
|  | Numeric_seperator | 0.54 | unmatched | name=0.53, description=0.00, type=1.00, example=1.00 |
|  | genjb_comment | 0.52 | unmatched | name=0.31, description=0.34, type=1.00, example=1.00 |
|  | genjb_job_number | 0.61 | unmatched | DeepSeek+RAG: Best match by name and type; JOB_NUMBER corresponds to job_number in target.; knowledge_items=5; rule_baseline=(name=0.68, description=0.00, type=1.00, example=1.00) |
|  | genjb_qjob_job_code | 0.60 | unmatched | DeepSeek+RAG: Field name 'CO_JOB' suggests job code, and historical mappings show job_number in VOY and BOL records, but no direct match for 'genjb_qjob_job_code'. Highest scoring candidate with job-related name.; knowledge_items=5; rule_baseline=(name=0.50, description=0.31, type=1.00, example=1.00) |
|  | genjb_description | 0.66 | unmatched | name=0.56, description=0.42, type=1.00, example=1.00 |
|  | genjb_company_id | 0.55 | unmatched | name=0.52, description=0.07, type=1.00, example=1.00 |
|  | genjb_qsts_code | 0.64 | unmatched | name=0.67, description=0.15, type=1.00, example=1.00 |
|  | genjb_qstsx_definition | 0.63 | unmatched | name=0.44, description=0.54, type=1.00, example=1.00 |
| EVEN_TASK.PROCESS_DATE | process_date | 0.80 | need_review | DeepSeek+RAG: Exact name match with target field 'process_date' and compatible datetime type.; knowledge_items=5; rule_baseline=(name=0.59, description=0.21, type=0.00, example=1.00) |
|  | CNI_docs_to_print | 0.58 | unmatched | name=0.62, description=0.00, type=1.00, example=1.00 |
|  | genjbde_nad_name_1 | 0.64 | unmatched | DeepSeek+RAG: Highest scoring candidate field with name containing 'NAME' and description 'D NAME', likely representing sender name.; knowledge_items=5; rule_baseline=(name=0.56, description=0.33, type=1.00, example=1.00) |
|  | genjbde_nad_name_2 | 0.63 | unmatched | DeepSeek+RAG: Highest scoring candidate field with 'name' in field name and description, suitable for sender name 2.; knowledge_items=5; rule_baseline=(name=0.56, description=0.31, type=1.00, example=1.00) |
|  | genjbde_nad_street_1 | 0.60 | unmatched | name=0.39, description=0.52, type=1.00, example=1.00 |
|  | genjbde_nad_street_2 | 0.60 | unmatched | name=0.39, description=0.48, type=1.00, example=1.00 |
|  | genjbde_nad_postal_code | 0.67 | unmatched | name=0.57, description=0.44, type=1.00, example=1.00 |
| BSCODE.LOCATION | genjbde_nad_location | 0.74 | need_review | DeepSeek+RAG: Highest scoring candidate field with name and description matching 'location'.; knowledge_items=5; rule_baseline=(name=0.69, description=0.53, type=1.00, example=1.00) |
|  | genjbde_nad_country_iso_code | 0.67 | unmatched | DeepSeek+RAG: Best match by name and description for country ISO code.; knowledge_items=5; rule_baseline=(name=0.62, description=0.35, type=1.00, example=1.00) |
|  | qnbr_number_code | 0.63 | unmatched | DeepSeek+RAG: EDI_CODE matches the 'OLS' code concept for address ID, and the field is required, aligning with the target requirement.; knowledge_items=5; rule_baseline=(name=0.55, description=0.34, type=1.00, example=1.00) |
|  | qnbrx_definition | 0.57 | unmatched | name=0.41, description=0.35, type=1.00, example=1.00 |
|  | nbr_value | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | cni_description | 0.61 | unmatched | name=0.52, description=0.30, type=1.00, example=1.00 |
|  | qtp0_type_0_code | 0.61 | unmatched | name=0.52, description=0.31, type=1.00, example=1.00 |
|  | qtp0x_definition | 0.60 | unmatched | name=0.56, description=0.18, type=1.00, example=1.00 |
|  | qtp1_type_1_code | 0.58 | unmatched | name=0.52, description=0.21, type=1.00, example=1.00 |
|  | qtp1x_definition | 0.59 | unmatched | name=0.43, description=0.39, type=1.00, example=1.00 |
|  | qtp2_type_2_code | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | qtp2x_definition | 0.54 | unmatched | name=0.39, description=0.27, type=1.00, example=1.00 |
|  | qtp3_type_3_code | 0.58 | unmatched | name=0.52, description=0.21, type=1.00, example=1.00 |
|  | qtp3x_definition | 0.59 | unmatched | name=0.39, description=0.44, type=1.00, example=1.00 |
|  | qtp4_type_4_code | 0.57 | unmatched | name=0.52, description=0.16, type=1.00, example=1.00 |
|  | qtp4x_definition | 0.53 | unmatched | name=0.47, description=0.07, type=1.00, example=1.00 |
|  | qtp5_type_5_code | 0.61 | unmatched | name=0.42, description=0.48, type=1.00, example=1.00 |
|  | qtp5x_definition | 0.60 | unmatched | name=0.33, description=0.62, type=1.00, example=1.00 |
|  | cni_traffic_code | 0.60 | unmatched | name=0.60, description=0.11, type=1.00, example=1.00 |
|  | cni_traffic_definition | 0.56 | unmatched | name=0.37, description=0.38, type=1.00, example=1.00 |
|  | cni_status_code | 0.65 | unmatched | name=0.69, description=0.16, type=1.00, example=1.00 |
|  | cni_file_manager | 0.61 | unmatched | name=0.69, description=0.00, type=1.00, example=1.00 |
|  | cni_activity_code | 0.65 | unmatched | name=0.67, description=0.18, type=1.00, example=1.00 |
|  | cnict_container_number | 0.67 | unmatched | name=0.82, description=0.00, type=1.00, example=1.00 |
|  | qcntst_code | 0.66 | unmatched | name=0.72, description=0.13, type=1.00, example=1.00 |
|  | qcntstx_definition | 0.59 | unmatched | name=0.38, description=0.47, type=1.00, example=1.00 |
|  | qcnts_container_size_code | 0.65 | unmatched | name=0.65, description=0.23, type=1.00, example=1.00 |
|  | qcntsx_definition | 0.63 | unmatched | name=0.47, description=0.47, type=1.00, example=1.00 |
|  | qcntt_container_type_code | 0.62 | unmatched | name=0.72, description=0.00, type=1.00, example=1.00 |
|  | qcnttx_definition | 0.63 | unmatched | name=0.47, description=0.47, type=1.00, example=1.00 |
|  | qcnth_container_height_code | 0.59 | unmatched | name=0.52, description=0.23, type=1.00, example=1.00 |
|  | qcnthx_definition | 0.63 | unmatched | name=0.47, description=0.49, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.55 | unmatched | name=0.53, description=0.06, type=1.00, example=1.00 |
|  | qrefx_definition | 0.58 | unmatched | name=0.39, description=0.43, type=1.00, example=1.00 |
|  | cnire_value | 0.61 | unmatched | name=0.52, description=0.31, type=1.00, example=1.00 |
|  | wmsordl3_line_number | 0.57 | unmatched | name=0.56, description=0.05, type=1.00, example=1.00 |
| GFBLAMS.ACI_REPORTNUMBER | wmsar_article_number | 0.71 | need_review | name=0.55, description=0.65, type=1.00, example=1.00 |
|  | wmsordst_number_order | 0.57 | unmatched | name=0.55, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_order_qmus_measure_code | 0.61 | unmatched | name=0.51, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_wmswc_warehouse_complex_code | 0.52 | unmatched | name=0.44, description=0.08, type=1.00, example=1.00 |
|  | wmsordst_1_wmswcx_definition | 0.53 | unmatched | name=0.29, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_wmswa_warehouse_code | 0.55 | unmatched | name=0.52, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_1_wmswax_description | 0.63 | unmatched | name=0.53, description=0.36, type=1.00, example=1.00 |
|  | wmsordst_1_wmswu_warehouse_unit_code | 0.56 | unmatched | name=0.54, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_1_wmswux_definition | 0.54 | unmatched | name=0.37, description=0.30, type=1.00, example=1.00 |
|  | wmsordst_1_wmswl_warehouse_location_code | 0.59 | unmatched | name=0.48, description=0.31, type=1.00, example=1.00 |
|  | wmsordst_1_wmswlx_description | 0.63 | unmatched | name=0.53, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_lot_number_1 | 0.54 | unmatched | name=0.37, description=0.30, type=1.00, example=1.00 |
|  | wmsordst_1_serial_number_1 | 0.56 | unmatched | name=0.58, description=0.00, type=1.00, example=1.00 |
|  | wmsordst_1_qcus_code | 0.59 | unmatched | name=0.53, description=0.20, type=1.00, example=1.00 |
|  | wmsordst_1_qcusx_definition | 0.55 | unmatched | name=0.36, description=0.36, type=1.00, example=1.00 |
|  | wmsordst_1_qreg_regime_code | 0.63 | unmatched | name=0.49, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_qregx_definition | 0.54 | unmatched | name=0.33, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_qsts_code | 0.57 | unmatched | name=0.56, description=0.08, type=1.00, example=1.00 |
|  | wmsordst_1_qstsx_definition | 0.55 | unmatched | name=0.29, description=0.46, type=1.00, example=1.00 |
|  | wmsordto_Tot_gross_weight | 0.61 | unmatched | name=0.42, description=0.50, type=1.00, example=1.00 |
|  | wmsordto_Tot_Net_weight | 0.63 | unmatched | name=0.44, description=0.53, type=1.00, example=1.00 |
|  | wmsordto_Tot_Volume | 0.63 | unmatched | name=0.43, description=0.56, type=1.00, example=1.00 |
|  | wmsordd_weight_qmus_measure_code | 0.56 | unmatched | name=0.47, description=0.18, type=1.00, example=1.00 |
|  | wmsordd_volume_qmus_measure_code | 0.57 | unmatched | name=0.43, description=0.29, type=1.00, example=1.00 |
|  | wmsordd_volume | 0.65 | unmatched | name=0.69, description=0.55, type=1.00, example=0.00 |
|  | wmsordd_length | 0.53 | unmatched | name=0.35, description=0.27, type=1.00, example=1.00 |
|  | wmsordd_width | 0.62 | unmatched | name=0.64, description=0.11, type=1.00, example=1.00 |
|  | wmsordd_height | 0.57 | unmatched | name=0.60, description=0.00, type=1.00, example=1.00 |
|  | wmsardc_definition | 0.62 | unmatched | name=0.38, description=0.59, type=1.00, example=1.00 |
|  | qftx_free_text_code | 0.58 | unmatched | name=0.53, description=0.19, type=1.00, example=1.00 |
|  | qftxx_definition | 0.60 | unmatched | name=0.35, description=0.55, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.56 | unmatched | name=0.53, description=0.08, type=1.00, example=1.00 |
|  | qrefx_definition | 0.58 | unmatched | name=0.39, description=0.43, type=1.00, example=1.00 |
|  | cnire_value | 0.59 | unmatched | name=0.52, description=0.25, type=1.00, example=1.00 |
|  | cnitmm_voyage_number | 0.57 | unmatched | name=0.60, description=0.00, type=1.00, example=1.00 |
|  | cnitmm_vessel_name | 0.62 | unmatched | name=0.59, description=0.19, type=1.00, example=1.00 |
|  | qloc_location_qual | 0.58 | unmatched | name=0.61, description=0.03, type=1.00, example=1.00 |
|  | cnipl_country_country_code | 0.57 | unmatched | name=0.51, description=0.14, type=1.00, example=1.00 |
|  | cnipl_locode_location_code | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | qdoc_code | 0.61 | unmatched | name=0.61, description=0.12, type=1.00, example=1.00 |
|  | cnido_document_number | 0.56 | unmatched | name=0.58, description=0.00, type=1.00, example=1.00 |
|  | cnido_place_of_issue | 0.59 | unmatched | name=0.50, description=0.26, type=1.00, example=1.00 |
|  | cnido_date_of_issue | 0.43 | unmatched | name=0.57, description=0.30, type=0.00, example=1.00 |

## Need Human Review

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
| EVEN_TASK.PROCESS_DATE | process_date | 0.80 | need_review | DeepSeek+RAG: Exact name match with target field 'process_date' and compatible datetime type.; knowledge_items=5; rule_baseline=(name=0.59, description=0.21, type=0.00, example=1.00) |
| BSCODE.LOCATION | genjbde_nad_location | 0.74 | need_review | DeepSeek+RAG: Highest scoring candidate field with name and description matching 'location'.; knowledge_items=5; rule_baseline=(name=0.69, description=0.53, type=1.00, example=1.00) |
| GFBLAMS.ACI_REPORTNUMBER | wmsar_article_number | 0.71 | need_review | name=0.55, description=0.65, type=1.00, example=1.00 |

## Unmatched API Fields

| db_column | api_param_path | confidence | status | reason |
|---|---|---:|---|---|
|  | Decimal_point | 0.60 | unmatched | DeepSeek+RAG: Field name 'LOCAL_DECIMAL_POINT' matches target 'Decimal_point' semantics; description '本幣小數位' (local currency decimal places) aligns with decimal marker usage.; knowledge_items=1; rule_baseline=(name=0.50, description=0.31, type=1.00, example=1.00) |
|  | Numeric_seperator | 0.54 | unmatched | name=0.53, description=0.00, type=1.00, example=1.00 |
|  | genjb_comment | 0.52 | unmatched | name=0.31, description=0.34, type=1.00, example=1.00 |
|  | genjb_job_number | 0.61 | unmatched | DeepSeek+RAG: Best match by name and type; JOB_NUMBER corresponds to job_number in target.; knowledge_items=5; rule_baseline=(name=0.68, description=0.00, type=1.00, example=1.00) |
|  | genjb_qjob_job_code | 0.60 | unmatched | DeepSeek+RAG: Field name 'CO_JOB' suggests job code, and historical mappings show job_number in VOY and BOL records, but no direct match for 'genjb_qjob_job_code'. Highest scoring candidate with job-related name.; knowledge_items=5; rule_baseline=(name=0.50, description=0.31, type=1.00, example=1.00) |
|  | genjb_description | 0.66 | unmatched | name=0.56, description=0.42, type=1.00, example=1.00 |
|  | genjb_company_id | 0.55 | unmatched | name=0.52, description=0.07, type=1.00, example=1.00 |
|  | genjb_qsts_code | 0.64 | unmatched | name=0.67, description=0.15, type=1.00, example=1.00 |
|  | genjb_qstsx_definition | 0.63 | unmatched | name=0.44, description=0.54, type=1.00, example=1.00 |
|  | CNI_docs_to_print | 0.58 | unmatched | name=0.62, description=0.00, type=1.00, example=1.00 |
|  | genjbde_nad_name_1 | 0.64 | unmatched | DeepSeek+RAG: Highest scoring candidate field with name containing 'NAME' and description 'D NAME', likely representing sender name.; knowledge_items=5; rule_baseline=(name=0.56, description=0.33, type=1.00, example=1.00) |
|  | genjbde_nad_name_2 | 0.63 | unmatched | DeepSeek+RAG: Highest scoring candidate field with 'name' in field name and description, suitable for sender name 2.; knowledge_items=5; rule_baseline=(name=0.56, description=0.31, type=1.00, example=1.00) |
|  | genjbde_nad_street_1 | 0.60 | unmatched | name=0.39, description=0.52, type=1.00, example=1.00 |
|  | genjbde_nad_street_2 | 0.60 | unmatched | name=0.39, description=0.48, type=1.00, example=1.00 |
|  | genjbde_nad_postal_code | 0.67 | unmatched | name=0.57, description=0.44, type=1.00, example=1.00 |
|  | genjbde_nad_country_iso_code | 0.67 | unmatched | DeepSeek+RAG: Best match by name and description for country ISO code.; knowledge_items=5; rule_baseline=(name=0.62, description=0.35, type=1.00, example=1.00) |
|  | qnbr_number_code | 0.63 | unmatched | DeepSeek+RAG: EDI_CODE matches the 'OLS' code concept for address ID, and the field is required, aligning with the target requirement.; knowledge_items=5; rule_baseline=(name=0.55, description=0.34, type=1.00, example=1.00) |
|  | qnbrx_definition | 0.57 | unmatched | name=0.41, description=0.35, type=1.00, example=1.00 |
|  | nbr_value | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | cni_description | 0.61 | unmatched | name=0.52, description=0.30, type=1.00, example=1.00 |
|  | qtp0_type_0_code | 0.61 | unmatched | name=0.52, description=0.31, type=1.00, example=1.00 |
|  | qtp0x_definition | 0.60 | unmatched | name=0.56, description=0.18, type=1.00, example=1.00 |
|  | qtp1_type_1_code | 0.58 | unmatched | name=0.52, description=0.21, type=1.00, example=1.00 |
|  | qtp1x_definition | 0.59 | unmatched | name=0.43, description=0.39, type=1.00, example=1.00 |
|  | qtp2_type_2_code | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | qtp2x_definition | 0.54 | unmatched | name=0.39, description=0.27, type=1.00, example=1.00 |
|  | qtp3_type_3_code | 0.58 | unmatched | name=0.52, description=0.21, type=1.00, example=1.00 |
|  | qtp3x_definition | 0.59 | unmatched | name=0.39, description=0.44, type=1.00, example=1.00 |
|  | qtp4_type_4_code | 0.57 | unmatched | name=0.52, description=0.16, type=1.00, example=1.00 |
|  | qtp4x_definition | 0.53 | unmatched | name=0.47, description=0.07, type=1.00, example=1.00 |
|  | qtp5_type_5_code | 0.61 | unmatched | name=0.42, description=0.48, type=1.00, example=1.00 |
|  | qtp5x_definition | 0.60 | unmatched | name=0.33, description=0.62, type=1.00, example=1.00 |
|  | cni_traffic_code | 0.60 | unmatched | name=0.60, description=0.11, type=1.00, example=1.00 |
|  | cni_traffic_definition | 0.56 | unmatched | name=0.37, description=0.38, type=1.00, example=1.00 |
|  | cni_status_code | 0.65 | unmatched | name=0.69, description=0.16, type=1.00, example=1.00 |
|  | cni_file_manager | 0.61 | unmatched | name=0.69, description=0.00, type=1.00, example=1.00 |
|  | cni_activity_code | 0.65 | unmatched | name=0.67, description=0.18, type=1.00, example=1.00 |
|  | cnict_container_number | 0.67 | unmatched | name=0.82, description=0.00, type=1.00, example=1.00 |
|  | qcntst_code | 0.66 | unmatched | name=0.72, description=0.13, type=1.00, example=1.00 |
|  | qcntstx_definition | 0.59 | unmatched | name=0.38, description=0.47, type=1.00, example=1.00 |
|  | qcnts_container_size_code | 0.65 | unmatched | name=0.65, description=0.23, type=1.00, example=1.00 |
|  | qcntsx_definition | 0.63 | unmatched | name=0.47, description=0.47, type=1.00, example=1.00 |
|  | qcntt_container_type_code | 0.62 | unmatched | name=0.72, description=0.00, type=1.00, example=1.00 |
|  | qcnttx_definition | 0.63 | unmatched | name=0.47, description=0.47, type=1.00, example=1.00 |
|  | qcnth_container_height_code | 0.59 | unmatched | name=0.52, description=0.23, type=1.00, example=1.00 |
|  | qcnthx_definition | 0.63 | unmatched | name=0.47, description=0.49, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.55 | unmatched | name=0.53, description=0.06, type=1.00, example=1.00 |
|  | qrefx_definition | 0.58 | unmatched | name=0.39, description=0.43, type=1.00, example=1.00 |
|  | cnire_value | 0.61 | unmatched | name=0.52, description=0.31, type=1.00, example=1.00 |
|  | wmsordl3_line_number | 0.57 | unmatched | name=0.56, description=0.05, type=1.00, example=1.00 |
|  | wmsordst_number_order | 0.57 | unmatched | name=0.55, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_order_qmus_measure_code | 0.61 | unmatched | name=0.51, description=0.33, type=1.00, example=1.00 |
|  | wmsordst_1_wmswc_warehouse_complex_code | 0.52 | unmatched | name=0.44, description=0.08, type=1.00, example=1.00 |
|  | wmsordst_1_wmswcx_definition | 0.53 | unmatched | name=0.29, description=0.42, type=1.00, example=1.00 |
|  | wmsordst_1_wmswa_warehouse_code | 0.55 | unmatched | name=0.52, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_1_wmswax_description | 0.63 | unmatched | name=0.53, description=0.36, type=1.00, example=1.00 |
|  | wmsordst_1_wmswu_warehouse_unit_code | 0.56 | unmatched | name=0.54, description=0.07, type=1.00, example=1.00 |
|  | wmsordst_1_wmswux_definition | 0.54 | unmatched | name=0.37, description=0.30, type=1.00, example=1.00 |
|  | wmsordst_1_wmswl_warehouse_location_code | 0.59 | unmatched | name=0.48, description=0.31, type=1.00, example=1.00 |
|  | wmsordst_1_wmswlx_description | 0.63 | unmatched | name=0.53, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_lot_number_1 | 0.54 | unmatched | name=0.37, description=0.30, type=1.00, example=1.00 |
|  | wmsordst_1_serial_number_1 | 0.56 | unmatched | name=0.58, description=0.00, type=1.00, example=1.00 |
|  | wmsordst_1_qcus_code | 0.59 | unmatched | name=0.53, description=0.20, type=1.00, example=1.00 |
|  | wmsordst_1_qcusx_definition | 0.55 | unmatched | name=0.36, description=0.36, type=1.00, example=1.00 |
|  | wmsordst_1_qreg_regime_code | 0.63 | unmatched | name=0.49, description=0.44, type=1.00, example=1.00 |
|  | wmsordst_1_qregx_definition | 0.54 | unmatched | name=0.33, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option1_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option2_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option3_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option4_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_code | 0.61 | unmatched | name=0.39, description=0.53, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_definition | 0.58 | unmatched | name=0.41, description=0.37, type=1.00, example=1.00 |
|  | wmsordst_1_storage_option5_value | 0.61 | unmatched | name=0.38, description=0.57, type=1.00, example=1.00 |
|  | wmsordst_1_qsts_code | 0.57 | unmatched | name=0.56, description=0.08, type=1.00, example=1.00 |
|  | wmsordst_1_qstsx_definition | 0.55 | unmatched | name=0.29, description=0.46, type=1.00, example=1.00 |
|  | wmsordto_Tot_gross_weight | 0.61 | unmatched | name=0.42, description=0.50, type=1.00, example=1.00 |
|  | wmsordto_Tot_Net_weight | 0.63 | unmatched | name=0.44, description=0.53, type=1.00, example=1.00 |
|  | wmsordto_Tot_Volume | 0.63 | unmatched | name=0.43, description=0.56, type=1.00, example=1.00 |
|  | wmsordd_weight_qmus_measure_code | 0.56 | unmatched | name=0.47, description=0.18, type=1.00, example=1.00 |
|  | wmsordd_volume_qmus_measure_code | 0.57 | unmatched | name=0.43, description=0.29, type=1.00, example=1.00 |
|  | wmsordd_volume | 0.65 | unmatched | name=0.69, description=0.55, type=1.00, example=0.00 |
|  | wmsordd_length | 0.53 | unmatched | name=0.35, description=0.27, type=1.00, example=1.00 |
|  | wmsordd_width | 0.62 | unmatched | name=0.64, description=0.11, type=1.00, example=1.00 |
|  | wmsordd_height | 0.57 | unmatched | name=0.60, description=0.00, type=1.00, example=1.00 |
|  | wmsardc_definition | 0.62 | unmatched | name=0.38, description=0.59, type=1.00, example=1.00 |
|  | qftx_free_text_code | 0.58 | unmatched | name=0.53, description=0.19, type=1.00, example=1.00 |
|  | qftxx_definition | 0.60 | unmatched | name=0.35, description=0.55, type=1.00, example=1.00 |
|  | qref_custom_reference | 0.56 | unmatched | name=0.53, description=0.08, type=1.00, example=1.00 |
|  | qrefx_definition | 0.58 | unmatched | name=0.39, description=0.43, type=1.00, example=1.00 |
|  | cnire_value | 0.59 | unmatched | name=0.52, description=0.25, type=1.00, example=1.00 |
|  | cnitmm_voyage_number | 0.57 | unmatched | name=0.60, description=0.00, type=1.00, example=1.00 |
|  | cnitmm_vessel_name | 0.62 | unmatched | name=0.59, description=0.19, type=1.00, example=1.00 |
|  | qloc_location_qual | 0.58 | unmatched | name=0.61, description=0.03, type=1.00, example=1.00 |
|  | cnipl_country_country_code | 0.57 | unmatched | name=0.51, description=0.14, type=1.00, example=1.00 |
|  | cnipl_locode_location_code | 0.57 | unmatched | name=0.59, description=0.00, type=1.00, example=1.00 |
|  | qdoc_code | 0.61 | unmatched | name=0.61, description=0.12, type=1.00, example=1.00 |
|  | cnido_document_number | 0.56 | unmatched | name=0.58, description=0.00, type=1.00, example=1.00 |
|  | cnido_place_of_issue | 0.59 | unmatched | name=0.50, description=0.26, type=1.00, example=1.00 |
|  | cnido_date_of_issue | 0.43 | unmatched | name=0.57, description=0.30, type=0.00, example=1.00 |
