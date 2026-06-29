# EDI Mapping Agent MVP

面向企业系统集成场景的规则版 EDI Mapping Agent。用户上传源系统和目标系统字段说明及样例数据后，系统会生成字段映射表、转换规则、`transform.py`、`test_transform.py`，运行 pytest，并输出 `report.md`。

第一版以本地规则匹配为基础，可选接入 DeepSeek 做语义增强；不实现完整 EDIFACT/X12 标准，聚焦 CSV、Excel、JSON、Word 表格和文本型 PDF。

## 安装

```bash
cd edi-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如需启用 DeepSeek，在 `.env` 中配置：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
LLM_CANDIDATE_LIMIT=8
```

## 运行 FastAPI

```bash
uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/docs`，调用 `POST /mapping/run` 上传：

- source_fields.xlsx 或 .csv
- target_fields.xlsx 或 .csv
- source_sample.json
- target_sample.json

## 运行 Streamlit

```bash
streamlit run ui/streamlit_app.py
```

页面包含两个工作流：

- 字段文件映射：上传两个系统字段说明和样例 JSON，生成转换代码、测试和报告。
- 数据库到接口推送：上传我的系统数据库文档和目标系统接口说明文档，生成目标接口 payload 模板和数据库字段映射文档。接口说明支持 CSV、Excel、Word 表格和文本型 PDF 表格，可勾选 DeepSeek 语义增强。

## 使用 sample_data 运行规则工作流

```bash
python -c "from app.services.workflow import run_mapping_workflow; r=run_mapping_workflow('sample_data/source_fields.xlsx','sample_data/target_fields.xlsx','sample_data/source_sample.json','sample_data/target_sample.json'); print(r.report_path); print(r.pytest_output)"
```

生成文件位于：

- `workspace/generated/transform.py`
- `workspace/tests/test_transform.py`
- `workspace/reports/report.md`

## 运行测试

```bash
pytest -q
```

## 字段说明格式

字段说明 CSV/Excel 必须包含：

| field_name | description | type | required | example |
|---|---|---|---|---|
| order_id | Source order identifier | string | true | SO-1001 |

## 数据库到接口推送文档格式

数据库文档 CSV/Excel/Word/PDF 必须包含字段表：

| table_name | column_name | description | type | required | example |
|---|---|---|---|---|---|
| orders | order_no | Order number | string | true | SO-1001 |

也支持常见中文数据库字典列名，例如：`表名`、`字段名`、`字段说明`、`类型`、`允许空`、`默认值`。当 `允许空` 为 `√` 时，系统会自动转换为 `required=false`。

目标接口文档 CSV/Excel/Word/PDF 必须包含接口字段表：

| endpoint | method | param_path | param_name | description | type | required | example |
|---|---|---|---|---|---|---|---|
| /api/orders | POST | order.orderNo | orderNo | Order number | string | true | SO-1001 |

Word 文档请使用真实表格。PDF 目前支持可复制文本型 PDF，并建议字段表使用 `|` 分隔；扫描件 PDF 暂不支持 OCR。

运行 demo：

```bash
python -c "from app.services.api_push_workflow import run_api_push_mapping_workflow; r=run_api_push_mapping_workflow('sample_data/database_doc.xlsx','sample_data/target_api_doc.xlsx'); print(r.payload_template_path); print(r.mapping_report_path)"
```

启用 DeepSeek 的命令行 demo：

```bash
python -c "from app.services.api_push_workflow import run_api_push_mapping_workflow; r=run_api_push_mapping_workflow('sample_data/database_doc.xlsx','sample_data/target_api_doc.xlsx', use_llm=True, llm_max_targets=10); print(r.llm_message); print(r.mapping_report_path)"
```

生成文件：

- `workspace/generated/target_api_payload_template.json`
- `workspace/generated/mapping_review.xlsx`
- `workspace/reports/api_push_mapping_report.md`

## 映射审查闭环

「数据库到接口推送」执行完成后，页面会显示可编辑的映射审查表。用户可以修改：

- `confirmed_source_field`
- `review_decision`
- `review_note`

点击「保存人工确认到 RAG」后，`confirm` 和 `modify` 的记录会保存为 `historical_mapping`，后续映射会优先使用这些人工确认结果。

点击「下载 mapping_review.xlsx」可以导出审查工作簿，包含：

- `All mappings`
- `Need review`
- `Unmatched`
- `RAG evidence`

## RAG 背景知识库

Streamlit 页面包含「背景知识库」Tab，可以录入或上传补充知识。支持：

- 业务术语解释
- 字段别名
- 历史映射案例
- 固定值规则
- 枚举映射说明

知识会保存到：

- `workspace/knowledge/knowledge_items.json`

可导入的样例：

- `sample_data/rag_business_knowledge.md`
- `sample_data/historical_mappings.csv`

启用 DeepSeek 语义增强时，系统会先按目标接口字段检索相关知识，再把知识片段、候选数据库字段和接口字段一起发给 DeepSeek。

对于格式不固定的资料，可以勾选「使用 DeepSeek 自动分析这个知识文件」。系统会先把任意 Word/PDF/Excel/文本转换为原文，再由 DeepSeek 抽取结构化知识：

- `historical_mapping`：历史字段映射
- `fixed_value_rule`：固定值规则
- `enum_mapping`：枚举对照
- `transform_rule`：拆分、合并、格式化等转换规则
- `field_alias`：字段别名
- `glossary`：业务术语
- `business_context`：一般业务背景

在「数据库到接口推送」页面也可以直接上传补充资料，并选择是否让 DeepSeek 先分析资料。

目标系统的 sample 也可以作为 RAG 资料上传，例如：

- JSON payload 示例
- TXT/CSV flat file 示例
- Word/PDF 业务样例说明
- Excel 样例数据或映射备注

这些 sample 会被作为 `target_sample` 知识参与后续字段理解和 DeepSeek 映射增强。

系统会对最终 `source_field` 做数据库字段白名单校验：凡是不在数据库字典中的字段，都会被拒绝并降级为 `unmatched`，不会进入最终映射结果。人工确认保存到 RAG 时也会执行同样校验。

## 架构说明

核心模块都放在 `app/services`：

- `document_parser.py`：解析 CSV/Excel 字段说明为统一 `FieldSchema`
- `field_matcher.py`：用字段名、描述、类型、样例计算匹配置信度
- `rule_generator.py`：生成 direct、date_format、enum_mapping、default_value 等规则
- `code_generator.py`：生成可执行 `transform.py`
- `test_generator.py`：基于样例生成 pytest
- `test_runner.py`：执行 pytest 并捕获结果
- `report_generator.py`：生成可审查 Markdown 报告

后续接入 LangGraph 或大模型 API 时，可以把 matcher、rule generator 拆成独立节点，保留当前数据模型和产物接口。
