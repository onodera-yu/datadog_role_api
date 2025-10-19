"""
Datadog Role Information

Datadogのロール情報を取得・分析するPythonスクリプト

主な機能:
- 全権限の一覧表示
- 全ロールの一覧表示
- ロール名でのフィルタリング検索
- 特定ロールの権限詳細表示
- ロール権限分析（許可/未許可権限の分類・統計）

使用方法:
    環境変数を設定してスクリプトを実行
    export DD_SITE="https://api.datadoghq.com"
    export DD_API_KEY="your_api_key"
    export DD_APP_KEY="your_app_key"
    export ROLE_DATA_ATTRIBUTES_NAME="Datadog Admin Role"
    python datadog_roles.py

Author: Your Name
Version: 1.0
"""

import json
import os
from pathlib import Path
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.roles_api import RolesApi
from datadog_api_client.exceptions import ApiException

configuration = Configuration(
    host=os.environ.get("DD_SITE"),
    api_key={
        "apiKeyAuth": os.environ.get("DD_API_KEY"),
        "appKeyAuth": os.environ.get("DD_APP_KEY"),
    },
)

# デバッグモード設定
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"


def save_to_json(data, filename):
    """
    APIレスポンスをJSONファイルに保存します（デバッグモード時のみ）。

    Args:
        data: Datadog APIのレスポンスオブジェクト
        filename (str): 保存先のファイル名

    Returns:
        None
    """
    if not DEBUG:
        return

    # パストラバーサル対策: ファイル名を安全化
    safe_filename = Path(filename).name
    if not safe_filename or safe_filename.startswith("."):
        print(f"Error: Invalid filename {filename}")
        return

    try:
        with open(safe_filename, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Debug: Data saved to {safe_filename}")
    except (IOError, OSError) as e:
        print(f"Error saving file {safe_filename}: {e}")


def dd_list_permissions():
    """
    Datadogで利用可能な全ての権限を一覧表示します。

    DEBUG=trueの場合、結果はlist_permissions.jsonファイルに保存されます。

    Returns:
        dict or None: 権限一覧のデータ、エラー時はNone
    """
    try:
        with ApiClient(configuration) as api_client:
            api_instance = RolesApi(api_client)
            response = api_instance.list_permissions()
            save_to_json(response, "list_permissions.json")
            return response.to_dict()
    except ApiException as e:
        print(f"Error getting permissions: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def dd_list_roles():
    """
    Datadog組織内の全てのロールを一覧表示します。

    DEBUG=trueの場合、結果はlist_roles.jsonファイルに保存されます。

    Returns:
        dict or None: ロール一覧のデータ、エラー時はNone
    """
    try:
        with ApiClient(configuration) as api_client:
            api_instance = RolesApi(api_client)
            response = api_instance.list_roles()
            save_to_json(response, "list_roles.json")
            return response.to_dict()
    except ApiException as e:
        print(f"Error getting roles: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def dd_list_roles_with_filter(role_name=None):
    """
    ロール名でフィルタリングしたロールを一覧表示します。

    Args:
        role_name (str, optional): フィルタリングするロール名。未指定の場合は環境変数ROLE_DATA_ATTRIBUTES_NAMEを使用

    Returns:
        dict or None: フィルタリングされたロール一覧のデータ
    """
    role_filter = role_name or os.environ.get("ROLE_DATA_ATTRIBUTES_NAME")
    if not role_filter:
        print(
            "Role name not provided and ROLE_DATA_ATTRIBUTES_NAME environment variable not set"
        )
        return None

    try:
        with ApiClient(configuration) as api_client:
            api_instance = RolesApi(api_client)
            response = api_instance.list_roles(filter=role_filter)
            save_to_json(response, "filtered_roles.json")
            return response.to_dict()
    except ApiException as e:
        print(f"Error filtering roles: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def dd_list_role_permissions(role_id=None):
    """
    特定のロールに許可された権限を一覧表示します。

    Args:
        role_id (str, optional): ロールのUUID。未指定の場合は環境変数ROLE_DATA_IDを使用

    Returns:
        dict or None: ロール権限のデータ
    """
    target_role_id = role_id or os.environ.get("ROLE_DATA_ID")
    if not target_role_id:
        print("Role ID not provided and ROLE_DATA_ID environment variable not set")
        return None

    try:
        with ApiClient(configuration) as api_client:
            api_instance = RolesApi(api_client)
            response = api_instance.list_role_permissions(role_id=target_role_id)
            save_to_json(response, "role_permissions.json")
            return response.to_dict()
    except ApiException as e:
        print(f"Error getting role permissions: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def analyze_role_permissions(role_name, save_json=False):
    """
    指定されたロール名の権限を分析し、許可/未許可の権限を整理して出力します。

    Args:
        role_name (str): 分析するロール名
        save_json (bool): JSONファイルに結果を保存するかどうか

    Returns:
        dict or None: 分析結果、エラー時はNone
    """
    print(f"Analyzing role: {role_name}")

    # 1. 全権限を取得
    all_permissions = dd_list_permissions()
    if not all_permissions:
        print("Failed to get permissions")
        return None

    # 2. 指定ロールをフィルタリング
    filtered_roles = dd_list_roles_with_filter(role_name)
    if not filtered_roles or not filtered_roles.get("data"):
        print(f"Role '{role_name}' not found")
        return None

    # 可読性向上: ネストしたアクセスを分割
    role_data = filtered_roles["data"][0]
    role_attributes = role_data.get("attributes", {})
    role_id = role_data.get("id")
    role_display_name = role_attributes.get("name", "Unknown")

    if not role_id:
        print("Role ID not found in response")
        return None

    print(f"Found role: {role_display_name} (ID: {role_id})")

    # 3. ロールの権限を取得
    role_permissions = dd_list_role_permissions(role_id)
    if not role_permissions:
        print("Failed to get role permissions")
        return None

    # 4. 権限を突合（可読性向上）
    try:
        all_permission_names = {
            perm["attributes"]["name"]
            for perm in all_permissions.get("data", [])
            if perm.get("attributes", {}).get("name")
        }
        granted_permission_names = {
            perm["attributes"]["name"]
            for perm in role_permissions.get("data", [])
            if perm.get("attributes", {}).get("name")
        }
        denied_permission_names = all_permission_names - granted_permission_names
    except (KeyError, TypeError) as e:
        print(f"Error processing permissions data: {e}")
        return None

    # 5. 結果を整理
    result = {
        "role_name": role_display_name,
        "role_id": role_id,
        "granted_permissions": sorted(list(granted_permission_names)),
        "denied_permissions": sorted(list(denied_permission_names)),
        "total_permissions": len(all_permission_names),
        "granted_count": len(granted_permission_names),
        "denied_count": len(denied_permission_names),
    }

    # 結果を出力
    print(f"\n=== Role Analysis Results ===")
    print(f"Role: {result['role_name']}")
    print(f"Total permissions: {result['total_permissions']}")
    print(f"Granted: {result['granted_count']}")
    print(f"Denied: {result['denied_count']}")

    if save_json:
        try:
            with open("role_analysis.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("Analysis result saved to role_analysis.json")
        except (IOError, OSError) as e:
            print(f"Error saving analysis result: {e}")

    return result


def main():
    # 環境変数からロール名を取得、またはデフォルト値を使用
    role_name = os.environ.get("ROLE_DATA_ATTRIBUTES_NAME", "Datadog Admin Role")
    result = analyze_role_permissions(role_name, save_json=True)
    if result is None:
        print("Analysis failed")
        return 1
    return 0


if __name__ == "__main__":
    main()
