import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.storefront

scenarios("catalogue.feature", "account_variants.feature")
