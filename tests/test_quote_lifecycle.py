import pytest
from types import SimpleNamespace
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from warehouse_quote_app.app.services.quote_lifecycle import QuoteLifecycleService


@pytest.mark.asyncio
async def test_create_quote_triggers_crm(mock_async_db):
    quote = MagicMock(id=42, total_amount=Decimal("100.0"))
    repo = MagicMock()
    repo.create_quote = AsyncMock(return_value=quote)
    repo.to_response_model = AsyncMock(return_value="resp")
    repo.get = AsyncMock(return_value=quote)
    repo.list_quotes = AsyncMock(return_value=([], 0))

    customer_repo = MagicMock()
    customer_repo.get = AsyncMock(return_value=True)

    with (
        patch(
            "warehouse_quote_app.app.services.quote_lifecycle.CustomerRepository",
            return_value=customer_repo,
        ),
        patch("warehouse_quote_app.app.services.quote_lifecycle.CRMService") as crm_cls,
    ):
        crm = AsyncMock()
        crm_cls.return_value = crm
        service = QuoteLifecycleService(mock_async_db, repository=repo)
        data = SimpleNamespace(customer_id=1, quote_request={})
        await service.create_quote(data, created_by_id=5)

        crm.create_deal.assert_called_once()
        crm.update_deal_stage.assert_called_once()
        crm.create_interaction.assert_called_once()
