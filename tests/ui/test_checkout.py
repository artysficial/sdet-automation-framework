import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.storefront

scenarios("checkout.feature")
