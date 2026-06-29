# EDI Mapping Agent Report

## Field Mapping Table

| source_field | target_field | confidence | rule_type | status | reason |
|---|---|---:|---|---|---|
| order_id | order_id | 1.00 | direct | auto_confirmed | name=1.00, description=1.00, type=1.00, example=1.00 |
| customer_name | buyer_name | 0.84 | direct | need_review | name=0.70, description=0.93, type=1.00, example=1.00 |
| order_date | order_date | 0.90 | date_format | auto_confirmed | name=1.00, description=0.60, type=1.00, example=1.00 |
| amount | total_amount | 0.85 | direct | need_review | name=0.67, description=1.00, type=1.00, example=1.00 |
| currency | currency_code | 0.89 | direct | need_review | name=0.76, description=1.00, type=1.00, example=1.00 |
| status | order_status | 0.72 | enum_mapping | need_review | name=0.67, description=0.79, type=1.00, example=0.20 |

## Unmatched Fields

No unmatched fields.

## Need Human Review

| source_field | target_field | confidence | rule_type | status | reason |
|---|---|---:|---|---|---|
| customer_name | buyer_name | 0.84 | direct | need_review | name=0.70, description=0.93, type=1.00, example=1.00 |
| amount | total_amount | 0.85 | direct | need_review | name=0.67, description=1.00, type=1.00, example=1.00 |
| currency | currency_code | 0.89 | direct | need_review | name=0.76, description=1.00, type=1.00, example=1.00 |
| status | order_status | 0.72 | enum_mapping | need_review | name=0.67, description=0.79, type=1.00, example=0.20 |

## Generated Artifacts

- Transform code: `D:/Workspace/EDI Agent/edi-agent/workspace/generated/transform.py`
- Pytest file: `D:/Workspace/EDI Agent/edi-agent/workspace/tests/test_transform.py`

## Test Result

- Passed: `True`

```text
..                                                                       [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\cacheprovider.py:469
  D:\Workspace\EDI Agent\edi-agent\.venv\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path D:\Workspace\EDI Agent\edi-agent\.pytest_cache\v\cache\nodeids: [WinError 5] 拒绝访问。: 'D:\\Workspace\\EDI Agent\\edi-agent\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2 passed, 1 warning in 0.04s
```
