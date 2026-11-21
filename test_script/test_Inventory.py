from jsonpath import jsonpath
import pytest
from pathlib import Path

from util.case_util import case_parametrize
from util.assert_util import assert_response

case_path = str(Path(__file__).parent.parent / "data" / "Inventory")


class TestInventory:

    @pytest.mark.inventoryManagement
    @case_parametrize(case_path + "/inventory_init.yaml")
    def test_init_inventory(self, case_info, init_inventory, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=init_inventory, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.inventoryManagement
    @case_parametrize(case_path + "/inventory_restock.yaml")
    def test_restock_inventory(self, case_info, restock_inventory, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=restock_inventory, **request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.inventoryManagement
    @pytest.mark.smoke
    @case_parametrize(case_path + "/inventory_get.yaml")
    def test_get_inventory(self, case_info, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(**request)

        assert_response(resp, case_info["expected"])

    @pytest.mark.inventoryManagement
    @case_parametrize(case_path + "/inventory_get_logs.yaml")
    def test_get_inventory_logs(self, case_info, admin_token, http_client):

        request = case_info["request"]
        resp = http_client.send_all_request(token=admin_token, **request)

        assert_response(resp, case_info["expected"])
