"""Service for managing inflation rate data."""
from datetime import datetime
from typing import List, Dict
from pymongo.database import Database
from .base_service import BaseDataService
from src.database.models import InflationRate
from src.providers.world_bank import WorldBankClient


class InflationService(BaseDataService):
    """
    Service for managing inflation rate data.
    
    Note: Inflation data is typically released monthly by government agencies.
    This service provides methods to manually add inflation data as it's not
    commonly available through free APIs in real-time.
    """

    COUNTRY_TO_CURRENCY: Dict[str, str] = {
        "USA": "USD",
        "POL": "PLN",
        "DEU": "EUR",  # Germany uses EUR
        "EUU": "EUR",  # European Union aggregates, EUR
    }

    def __init__(self, db: Database):
        """Initialize inflation service."""
        super().__init__(db, "inflation_rates")
        self.client = WorldBankClient()
        self.create_indexes([[("date", 1), ("currency", 1)]])

    def add_inflation_rate(
        self,
        date: datetime,
        currency: str,
        rate: float,
        source: str = "manual"
    ) -> bool:
        """
        Add a single inflation rate record.
        
        Args:
            date: Date of the inflation rate (typically first day of month)
            currency: Currency code (USD, PLN, EUR)
            rate: Inflation rate as percentage
            source: Data source
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            record = InflationRate(
                date=date,
                currency=currency,
                rate=rate,
                source=source
            )
            
            self.collection.insert_one(record.model_dump())
            self.logger.info(f"Added inflation rate for {currency} on {date.date()}: {rate}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding inflation rate: {str(e)}")
            return False

    def add_inflation_rates_bulk(self, rates: List[dict]) -> int:
        """
        Add multiple inflation rate records.
        
        Args:
            rates: List of dictionaries with date, currency, rate, and optional source
            
        Returns:
            Number of records inserted
        """
        records = []
        for rate_data in rates:
            try:
                record = InflationRate(**rate_data)
                records.append(record.model_dump())
            except Exception as e:
                self.logger.error(f"Error validating inflation rate: {str(e)}")
                continue
        
        return self.bulk_insert(records)

    def update_inflation_from_world_bank(self) -> dict:
        """Fetch and upsert annual CPI inflation for USA, Poland, Germany, EU.

        Indicator: FP.CPI.TOTL.ZG
        """
        countries = ["USA", "POL", "DEU", "EUU"]
        stats = {"total_inserted": 0, "countries_updated": 0}
        end_date = datetime.now()

        for country in countries:
            currency = self.COUNTRY_TO_CURRENCY[country]
            # Determine start year based on latest existing record for currency
            latest = self.collection.find_one({"currency": currency}, sort=[("date", -1)])
            if latest:
                start_year = latest["date"].year + 1
            else:
                start_year = end_date.year - 10  # fetch last 10 years initially

            self.logger.info(f"Fetching World Bank CPI for {country} -> {currency} from {start_year}")
            series = self.client.fetch_inflation_cpi_annual(country)
            if not series:
                self.logger.warning(f"No inflation data returned for {country}")
                continue

            # Build records for missing years
            records: List[dict] = []
            for item in series:
                year = item["year"]
                value = item["value"]
                if year < start_year or year > end_date.year:
                    continue
                if value is None:
                    continue
                record = InflationRate(
                    date=datetime(year, 1, 1),
                    currency=currency,
                    rate=float(value),
                    source="worldbank"
                )
                records.append(record.model_dump())

            if records:
                inserted = self.bulk_insert(records)
                stats["total_inserted"] += inserted
                stats["countries_updated"] += 1

        return stats

    def get_latest_rate(self, currency: str) -> dict:
        """
        Get the latest inflation rate for a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Latest inflation rate record or None
        """
        return self.collection.find_one(
            {"currency": currency},
            sort=[("date", -1)]
        )

    def get_rates_by_currency(
        self,
        currency: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[dict]:
        """
        Get inflation rates for a currency within a date range.
        
        Args:
            currency: Currency code
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of inflation rate records
        """
        query = {"currency": currency}
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        
        return list(self.collection.find(query).sort("date", 1))

    def seed_sample_data(self):
        """
        Seed some sample inflation data for testing.
        This is for demonstration purposes only.
        """
        # Sample data (replace with actual inflation data)
        sample_data = [
            {"date": datetime(2024, 1, 1), "currency": "USD", "rate": 3.4, "source": "sample"},
            {"date": datetime(2024, 2, 1), "currency": "USD", "rate": 3.2, "source": "sample"},
            {"date": datetime(2024, 3, 1), "currency": "USD", "rate": 3.5, "source": "sample"},
            {"date": datetime(2024, 1, 1), "currency": "EUR", "rate": 2.8, "source": "sample"},
            {"date": datetime(2024, 2, 1), "currency": "EUR", "rate": 2.6, "source": "sample"},
            {"date": datetime(2024, 3, 1), "currency": "EUR", "rate": 2.4, "source": "sample"},
            {"date": datetime(2024, 1, 1), "currency": "PLN", "rate": 4.9, "source": "sample"},
            {"date": datetime(2024, 2, 1), "currency": "PLN", "rate": 4.6, "source": "sample"},
            {"date": datetime(2024, 3, 1), "currency": "PLN", "rate": 4.3, "source": "sample"},
        ]
        
        try:
            return self.add_inflation_rates_bulk(sample_data)
        except Exception as e:
            self.logger.error(f"Error seeding sample data: {str(e)}")
            return 0

