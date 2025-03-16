import unittest
import logging
from decimal import Decimal
from datetime import datetime, timezone
from warehouse_quote_app.app.services.business.rate_calculator import RateCalculator, StorageRequest, ServiceDimensions
from warehouse_quote_app.app.services.quote_service import QuoteRequest, QuoteService

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestComplexStorageQuote(unittest.TestCase):
    def setUp(self):
        self.quote_service = QuoteService()
        self.rate_calculator = RateCalculator()
        logger.info("=== Starting new test case ===")

    def test_complex_warehouse_quote(self):
        """
        Test case for a complex warehouse quote with:
        - Floor space for bulky items (500-1000m²)
        - Pallet storage (500-1000 spaces)
        - Volume-based storage for tall items
        - DG storage for lithium batteries
        """
        logger.info("Testing minimum space requirement scenario")
        
        # Test minimum space requirement
        min_quote_request = QuoteRequest(
            services=["storage"],
            company_name="Test Heavy Equipment Co",
            storage_type="mixed",  # Both floor and pallet storage
            duration_weeks=52,  # 12 months
            dimensions=ServiceDimensions(
                floor_space_m2=500.0,  # Minimum floor space
                pallet_spaces=500,  # Minimum pallet spaces
                has_oversized=True
            ),
            has_dangerous_goods=True,  # For lithium batteries
            special_instructions="DG storage required for lithium batteries (8 pallets)"
        )

        logger.debug(f"Minimum quote request parameters: {min_quote_request}")
        min_response = self.quote_service.process_quote_request(min_quote_request)
        logger.debug(f"Minimum quote response: {min_response}")
        
        # Validate minimum space costs
        expected_min_weekly_floor = Decimal('8750.00')  # 500m² × $2.50 × 7 days
        expected_min_weekly_pallet = Decimal('2500.00')  # 500 pallets × $5.00
        expected_min_total = expected_min_weekly_floor + expected_min_weekly_pallet
        
        logger.info("Validating minimum space costs:")
        logger.info(f"Expected floor cost: ${expected_min_weekly_floor}")
        logger.info(f"Expected pallet cost: ${expected_min_weekly_pallet}")
        logger.info(f"Expected total: ${expected_min_total}")
        logger.info(f"Actual total: ${min_response.total_amount}")
        
        self.assertEqual(min_response.total_amount, expected_min_total)
        
        logger.info("Testing maximum space requirement scenario")
        
        # Test maximum space requirement
        max_quote_request = QuoteRequest(
            services=["storage"],
            company_name="Test Heavy Equipment Co",
            storage_type="mixed",
            duration_weeks=52,
            dimensions=ServiceDimensions(
                floor_space_m2=1000.0,  # Maximum floor space
                pallet_spaces=1000,  # Maximum pallet spaces
                has_oversized=True
            ),
            has_dangerous_goods=True
        )

        logger.debug(f"Maximum quote request parameters: {max_quote_request}")
        max_response = self.quote_service.process_quote_request(max_quote_request)
        logger.debug(f"Maximum quote response: {max_response}")
        
        # Validate maximum space costs
        expected_max_weekly_floor = Decimal('17500.00')  # 1000m² × $2.50 × 7 days
        expected_max_weekly_pallet = Decimal('5000.00')  # 1000 pallets × $5.00
        expected_max_total = expected_max_weekly_floor + expected_max_weekly_pallet
        
        logger.info("Validating maximum space costs:")
        logger.info(f"Expected floor cost: ${expected_max_weekly_floor}")
        logger.info(f"Expected pallet cost: ${expected_max_weekly_pallet}")
        logger.info(f"Expected total: ${expected_max_total}")
        logger.info(f"Actual total: ${max_response.total_amount}")
        
        self.assertEqual(max_response.total_amount, expected_max_total)

        logger.info("Testing handling fees and DG surcharges")
        
        # Test handling fees
        handling_request = StorageRequest(
            dimensions=ServiceDimensions(
                pallet_spaces=8  # DG pallets
            ),
            storage_type="pallet",
            duration_weeks=1,
            quantity=8,
            dangerous_goods=True
        )

        logger.debug(f"Handling request parameters: {handling_request}")
        handling_response = self.rate_calculator.calculate_handling_fees(handling_request)
        logger.debug(f"Handling response: {handling_response}")
        
        # Validate handling fees
        expected_handling = Decimal('80.00')  # 8 pallets × $10 handling
        expected_dg_surcharge = Decimal('120.00')  # 8 pallets × $15 DG surcharge
        expected_total_handling = expected_handling + expected_dg_surcharge
        
        logger.info("Validating handling fees:")
        logger.info(f"Expected handling fee: ${expected_handling}")
        logger.info(f"Expected DG surcharge: ${expected_dg_surcharge}")
        logger.info(f"Expected total handling: ${expected_total_handling}")
        logger.info(f"Actual total handling: ${handling_response.total_amount}")
        
        self.assertEqual(handling_response.total_amount, expected_total_handling)

        logger.info("Testing volume-based storage calculations")
        
        # Test volume-based storage for tall item
        volume_request = StorageRequest(
            dimensions=ServiceDimensions(
                length=9.02,
                width=3.76,
                height=3.31,
                calculate_volume=True
            ),
            duration_weeks=1,
            quantity=1,
            storage_type="volume",
            dangerous_goods=False
        )
        
        logger.debug(f"Volume request parameters: {volume_request}")
        volume_line_items = self.rate_calculator.calculate_storage_costs(volume_request)
        logger.debug(f"Volume response: {volume_line_items}")
        
        # Validate volume-based storage
        expected_volume = Decimal('112.33')  # 9.02 × 3.76 × 3.31
        expected_weekly_cost = expected_volume * Decimal('4.00')  # $4.00/m³/week
        
        # Get the actual cost from the first line item
        actual_weekly_cost = volume_line_items[0].amount
        logger.info(f"Actual weekly cost: ${actual_weekly_cost}")
        
        self.assertAlmostEqual(
            actual_weekly_cost,
            expected_weekly_cost,
            places=2,
            msg="Volume-based storage cost calculation incorrect"
        )

    def test_messages_and_validations(self):
        """Test business rules and messages for the complex storage quote"""
        logger.info("Testing business rules and validation messages")
        
        quote_request = QuoteRequest(
            services=["storage"],
            company_name="Test Heavy Equipment Co",
            storage_type="mixed",
            duration_weeks=52,
            dimensions=ServiceDimensions(
                floor_space_m2=500.0,
                pallet_spaces=500,
                has_oversized=True
            ),
            has_dangerous_goods=True
        )

        logger.debug(f"Validation test request parameters: {quote_request}")
        response = self.quote_service.process_quote_request(quote_request)
        logger.debug(f"Validation test response: {response}")

        # Validate DG warning messages
        dg_messages = [msg for msg in response.messages if "dangerous goods" in msg.lower()]
        logger.info(f"DG warning messages: {dg_messages}")
        self.assertTrue(len(dg_messages) > 0, "Should include DG warning messages")

        # Validate storage duration messages
        duration_messages = [msg for msg in response.messages if any(term in msg.lower() for term in ["12+ months", "12 months"])]
        logger.info(f"Duration messages: {duration_messages}")
        self.assertTrue(len(duration_messages) > 0, "Should include storage duration messages")

        # Validate oversized item handling messages
        oversized_messages = [msg for msg in response.messages if "oversized" in msg.lower()]
        logger.info(f"Oversized handling messages: {oversized_messages}")
        self.assertTrue(len(oversized_messages) > 0, "Should include oversized handling messages")

if __name__ == '__main__':
    unittest.main(verbosity=2)
