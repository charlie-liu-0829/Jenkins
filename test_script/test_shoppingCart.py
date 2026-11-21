from jsonpath import jsonpath
import pytest
from pathlib import Path

from util.case_util import case_parametrize
from util.assert_util import assert_response

case_path = str(Path(__file__).parent.parent / "data" / "shoppingCart")


class TestShoppingCart:
    @pytest.mark.shoppingCart
    @case_parametrize(case_path + "/shopping_add.yaml")
    def test_add_shopping(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.shoppingCart
    @case_parametrize(case_path + "/shopping_update.yaml")
    def test_update_shopping(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.shoppingCart
    @case_parametrize(case_path + "/shopping_del.yaml")
    def test_del_shopping(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.shoppingCart
    @case_parametrize(case_path + "/shopping_check.yaml")
    def test_check_shopping(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.shoppingCart
    @case_parametrize(case_path + "/shopping_clear.yaml")
    def test_clear_shopping(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])
