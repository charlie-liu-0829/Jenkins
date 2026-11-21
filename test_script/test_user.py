from jsonpath import jsonpath
import pytest
from pathlib import Path

from util.case_util import case_parametrize
from util.assert_util import assert_response
from util.api_setup import api_url, response_value

case_path = str(Path(__file__).parent.parent / "data" / "user")


class TestUser:

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_register.yaml")
    def test_register(self, case_info, registered_user_cleanup, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(**request)
        if jsonpath(resp.json(), "$.code")[0] == 0:
            registered_user_cleanup(request["json"]["phone"])

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @pytest.mark.smoke
    @case_parametrize(case_path + "/user_login.yaml")
    def test_login(self, case_info, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(**request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_log_out.yaml")
    def test_log_out(self, user_token, case_info, http_client):

        # 请求信息：POST，无请求体，Authorization Bearer token
        request: dict = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_change_password.yaml")
    def test_change_password(self, change_pwd_user, case_info, http_client):

        request: dict = case_info["request"]
        resp = http_client.send_all_request(token=change_pwd_user, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @pytest.mark.smoke
    @case_parametrize(case_path + "/user_get_info.yaml")
    def test_get_info(self, user_token, case_info, http_client):

        request: dict = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])


class TestAddresses:
    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_get_addresses.yaml")
    def test_get_addresses_info(self, user_token, case_info, http_client):

        request: dict = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_add_addresses.yaml")
    def test_add_addresses(self, user_token, case_info, http_client, address_cleanup):

        request: dict = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)
        if resp.json().get("code") == 0:
            address_cleanup(response_value(resp, "$.data.addressId"))

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_change_addresses.yaml")
    def test_change_addresses(
        self, user_token, case_info, http_client, address_resource
    ):

        request = {
            **case_info["request"],
            "url": api_url(f"/api/users/addresses/{address_resource.resource_id}"),
        }
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_set_default_addresses.yaml")
    def test_set_default_addresses(
        self, user_token, case_info, http_client, address_resource
    ):

        request = {
            **case_info["request"],
            "url": api_url(
                f"/api/users/addresses/{address_resource.resource_id}/default"
            ),
        }
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.userManager
    @case_parametrize(case_path + "/user_del_addresses.yaml")
    def test_del_addresses(self, user_token, case_info, http_client, address_resource):

        request = {
            **case_info["request"],
            "url": api_url(f"/api/users/addresses/{address_resource.resource_id}"),
        }
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])
