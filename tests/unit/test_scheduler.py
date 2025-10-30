"""Unit tests for scheduler."""

from unittest.mock import Mock, patch

import pytest

from src.scheduler.data_scheduler import DataScheduler


@pytest.mark.unit
class TestDataScheduler:
    """Tests for DataScheduler."""

    def test_init(self, mock_db):
        """Test scheduler initialization."""
        scheduler = DataScheduler(mock_db)
        assert scheduler.db == mock_db
        assert scheduler.scheduler is not None
        assert "exchange_rates" in scheduler.services
        assert "gold_prices" in scheduler.services
        assert "stock_prices" in scheduler.services

    @patch("src.scheduler.data_scheduler.BackgroundScheduler")
    def test_start(self, mock_scheduler_class, mock_db):
        """Test starting scheduler."""
        mock_scheduler_instance = Mock()
        mock_scheduler_class.return_value = mock_scheduler_instance

        scheduler = DataScheduler(mock_db)
        scheduler.start()

        mock_scheduler_instance.start.assert_called_once()

    @patch("src.scheduler.data_scheduler.BackgroundScheduler")
    def test_stop(self, mock_scheduler_class, mock_db):
        """Test stopping scheduler."""
        mock_scheduler_instance = Mock()
        mock_scheduler_instance.running = True
        mock_scheduler_class.return_value = mock_scheduler_instance

        scheduler = DataScheduler(mock_db)
        scheduler.stop()

        mock_scheduler_instance.shutdown.assert_called_once()

    def test_run_now(self, mock_db):
        """Test run_now method."""
        scheduler = DataScheduler(mock_db)

        with patch.object(scheduler, "update_all_data") as mock_update:
            scheduler.run_now()
            mock_update.assert_called_once()

    def test_update_all_data(self, mock_db):
        """Test update_all_data method."""
        scheduler = DataScheduler(mock_db)

        # Mock the service update methods
        scheduler.services["exchange_rates"].update_all_pairs = Mock(return_value={"total_inserted": 10})
        scheduler.services["gold_prices"].update_gold_prices = Mock(return_value={"total_inserted": 5})
        scheduler.services["stock_prices"].update_sp500 = Mock(return_value={"total_inserted": 3})

        # Call update_all_data
        scheduler.update_all_data()

        # Verify all services were called
        scheduler.services["exchange_rates"].update_all_pairs.assert_called_once()
        scheduler.services["gold_prices"].update_gold_prices.assert_called_once()
        scheduler.services["stock_prices"].update_sp500.assert_called_once()

    def test_update_all_data_with_error(self, mock_db):
        """Test update_all_data with error."""
        scheduler = DataScheduler(mock_db)

        # Mock one service to raise an exception
        scheduler.services["exchange_rates"].update_all_pairs = Mock(side_effect=Exception("Test error"))

        # Should not raise exception - error is caught and logged
        scheduler.update_all_data()
