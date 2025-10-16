"""
List permissions returns "OK" response
"""

import json
from os import environ
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.roles_api import RolesApi

configuration = Configuration(
    host=environ.get("DD_SITE"),
    api_key={
        "apiKeyAuth": environ.get("DD_TEST_API_KEY"),
        "appKeyAuth": environ.get("DD_TEST_APP_KEY"),
    },
)

# デバッグモード設定
DEBUG = environ.get("DEBUG", "false").lower() == "true"


def save_to_json(data, filename):
    """
    APIレスポンスをJSONファイルに保存します（デバッグモード時のみ）。

    Args:
        data: Datadog APIのレスポンスオブジェクト
        filename (str): 保存先のファイル名

    Returns:
        None
    """
    if DEBUG:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Debug: Data saved to {filename}")


def datadog_list_permissions():
    """
    Datadogで利用可能な全ての権限を一覧表示します。

    DEBUG=trueの場合、結果はlist_permissions.jsonファイルに保存されます。

    Args:
        None

    Returns:
        dict: 権限一覧のデータ
    """
    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_permissions()
        save_to_json(response, "list_permissions.json")
        return response.to_dict()


def datadog_list_roles():
    """
    Datadog組織内の全てのロールを一覧表示します。

    DEBUG=trueの場合、結果はlist_roles.jsonファイルに保存されます。

    Args:
        None

    Returns:
        None
    """
    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_roles()
        save_to_json(response, "list_roles.json")


def datadog_list_roles_with_filter():
    """
    ROLE_DATA_ATTRIBUTES_NAME環境変数を使用してロール名でフィルタリングしたロールを一覧表示します。

    ROLE_DATA_ATTRIBUTES_NAMEには以下を設定できます：
    - 標準ロール: "Datadog Admin Role", "Datadog Standard Role", "Datadog Read Only Role"
    - カスタムロール: 組織で作成した任意のカスタムロール名
    - 部分一致: "Admin", "Read"などの部分的な名前

    DEBUG=trueの場合、結果はfiltered_roles.jsonファイルに保存されます。

    例:
        export ROLE_DATA_ATTRIBUTES_NAME="Datadog Admin Role"

    Args:
        None

    Returns:
        None
    """
    role_filter = environ.get("ROLE_DATA_ATTRIBUTES_NAME")
    if not role_filter:
        print("ROLE_DATA_ATTRIBUTES_NAME environment variable not set")
        return

    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_roles(filter=role_filter)
        save_to_json(response, "filtered_roles.json")


def datadog_list_role_permissions():
    """
    ROLE_DATA_ID環境変数を使用して、特定のロールに許可された権限を一覧表示します。

    ROLE_DATA_IDは、クエリを実行するロールのUUIDに設定する必要があります。
    ロールIDは、datadog_list_roles()関数の出力から取得できます。

    DEBUG=trueの場合、結果はrole_permissions.jsonファイルに保存されます。

    例:
        export ROLE_DATA_ID="12345678-1234-1234-1234-123456789abc"

    Args:
        None

    Returns:
        None
    """
    role_id = environ.get("ROLE_DATA_ID")
    if not role_id:
        print("ROLE_DATA_ID environment variable not set")
        return

    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_role_permissions(role_id=role_id)
        save_to_json(response, "role_permissions.json")


def main():
    # datadog_list_permissions()
    # datadog_list_roles()
    # datadog_list_roles_with_filter()
    datadog_list_role_permissions()


main()
