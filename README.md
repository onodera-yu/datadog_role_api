# Datadog Role Information

Datadogのロール情報を取得するPythonスクリプト

## 使用方法

1. config.jsonでAPIキーを設定:
```json
{
    "dd_api_key": "your_api_key_here",
    "dd_app_key": "your_app_key_here"
}
```

2. スクリプト実行:
```bash
python get_roles.py
```