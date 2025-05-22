import unittest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from warehouse_quote_app.app.database.session import Base
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.crm import Deal, DealStage
from warehouse_quote_app.app.models.quote import Quote

class TestQuoteDealRelationship(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def test_quote_associated_with_deal(self):
        session = self.Session()
        user = User(email="u@test.com", username="u", hashed_password="x")
        customer = Customer(name="cust", email="c@test.com", phone="123", address="street")
        session.add_all([user, customer])
        session.commit()

        deal = Deal(customer_id=customer.id, title="Deal", stage=DealStage.LEAD)
        session.add(deal)
        session.commit()

        quote = Quote(
            customer_id=customer.id,
            total_amount=Decimal("10.00"),
            service_type="storage",
            created_by=user.id,
            deal_id=deal.id,
        )
        session.add(quote)
        session.commit()
        session.refresh(quote)

        self.assertEqual(quote.deal_id, deal.id)
        self.assertIs(quote.deal, deal)
        self.assertIn(quote, deal.quotes)
        session.close()

if __name__ == "__main__":
    unittest.main()
