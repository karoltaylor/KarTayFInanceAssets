"""Unit tests for scheduler."""

from unittest.mock import MagicMock, Mock, patch

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
        mock_scheduler_class.return_value = mock_scheduler_instance

        scheduler = DataScheduler(mock_db)
        scheduler.stop()

        mock_scheduler_instance.shutdown.assert_called_once()

    def test_run_now(self, mock_db):
        """Test run_now method."""
        scheduler = DataScheduler(mock_db)

        with patch.object(scheduler, "_update_all_data") as mock_update:
            scheduler.run_now()
            mock_update.assert_called_once()

    def test_update_all_data(self, mock_db):
        """Test _update_all_data method."""
        scheduler = DataScheduler(mock_db)

        with patch("src.scheduler.data_scheduler.ExchangeRateService") as mock_ex:
            with patch("src.scheduler.data_scheduler.GoldPriceService") as mock_gold:
                with patch("src.scheduler.data_scheduler.StockPriceService") as mock_stock:
                    with patch("src.scheduler.data_scheduler.InflationService") as mock_inf:
                        mock_ex_instance = Mock()
                        mock_ex_instance.update_all_pairs.return_value = {"total_inserted": 10}
                        mock_ex.return_value = mock_ex_instance

                        mock_gold_instance = Mock()
                        mock_gold_instance.update_gold_prices.return_value = {"total_inserted": 5}
                        mock_gold.return_value = mock_gold_instance

                        mock_stock_instance = Mock()
                        mock_stock_instance.update_sp500.return_value = {"total_inserted": 3}
                        mock_stock.return_value = mock_stock_instance

                        mock_inf_instance = Mock()
                        mock_inf_instance.update_inflation_from_world_bank.return_value = {"countries_updated": 2}
                        mock_inf.return_value = mock_inf_instance

                        scheduler._update_all_data()

                        mock_ex_instance.update_all_pairs.assert_called_once()
                        mock_gold_instance.update_gold_prices.assert_called_once()
                        mock_stock_instance.update_sp500.assert_called_once()
                        mock_inf_instance.update_inflation_from_world_bank.assert_called_once()

    def test_update_all_data_with_error(self, mock_db):
        """Test _update_all_data with error."""
        scheduler = DataScheduler(mock_db)

        with patch("src.scheduler.data_scheduler.ExchangeRateService") as mock_ex:
            mock_ex.side_effect = Exception("Test error")

            # Should not raise exception
            scheduler._update_all_data()
