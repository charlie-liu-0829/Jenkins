from jsonpath import jsonpath
import pytest
from pathlib import Path

from util.api_setup import replace_path_id
from util.case_util import case_parametrize
from util.assert_util import assert_response

case_path = str(Path(__file__).parent.parent / "data" / "refund")


class TestRefund:

    @pytest.mark.refund
    @case_parametrize(case_path + "/refund_create.yaml")
    def test_create_refund(self, case_info, refund_create, http_client):

        request = case_info["request"]
        if case_info["expected"]["code"] == 0:
            request = replace_path_id(request, 14, refund_create.order_id)
        resp = http_client.send_all_request(token=refund_create.token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.refund
    @case_parametrize(case_path + "/refund_approve.yaml")
    def test_approve_refund(self, case_info, approve_refund, http_client):

        request = case_info["request"]
        if case_info["expected"]["code"] == 0:
            request = replace_path_id(request, 1, approve_refund.refund_id)
        resp = http_client.send_all_request(token=approve_refund.token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.refund
    @case_parametrize(case_path + "/refund_reject.yaml")
    def test_reject_refund(self, case_info, reject_refund, http_client):

        request = case_info["request"]
        if case_info["expected"]["code"] == 0:
            request = replace_path_id(request, 2, reject_refund.refund_id)
        resp = http_client.send_all_request(token=reject_refund.token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.refund
    @case_parametrize(case_path + "/refund_check.yaml")
    def test_check_refund(self, case_info, user_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=user_token, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.refund
    @case_parametrize(case_path + "/refund_check_all.yaml")
    def test_check_all_refund(self, case_info, admin_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=admin_token, **request)

        assert_response(resp, case_info["expected"])
