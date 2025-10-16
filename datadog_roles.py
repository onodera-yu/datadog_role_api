"""
List permissions returns "OK" response
"""

from os import environ
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.roles_api import RolesApi

configuration = Configuration(
    # host=environ.get("DD_SITE"),
    api_key={
        "apiKeyAuth": environ.get("DD_TEST_API_KEY"),
        "appKeyAuth": environ.get("DD_TEST_APP_KEY"),
    },
)

def datadog_list_permissions():
    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_permissions()

        print(response)

def datadog_list_roles():
    with ApiClient(configuration) as api_client:
        api_instance = RolesApi(api_client)
        response = api_instance.list_roles()

        print(response)

def main():
    # datadog_list_permissions()
    datadog_list_roles()

main()