import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from comstock_processor import ComStockProcessor


class TestComStockProcessor(unittest.TestCase):
    @patch("requests.get")
    def test_download_file_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"Test content"

        # get a temp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

        processor = ComStockProcessor("OR", "Multnomah County", "MediumOffice", "0", tmp_path)
        save_path = tmp_path / "test_file.parquet"

        processor.download_file("http://example.com/test_file.parquet", save_path)

        self.assertTrue(save_path.exists())
        with open(save_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"Test content")
        save_path.unlink()

    @patch("requests.get")
    def test_download_file_failure(self, mock_get):
        mock_get.return_value.status_code = 404

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            processor = ComStockProcessor("OR", "Multnomah County", "MediumOffice", "0", tmp_path)
            with patch("builtins.print") as mocked_print:
                processor.download_file("http://example.com/test_file.parquet", tmp_path / "test_file.parquet")
                mocked_print.assert_called_with("Failed to download file: http://example.com/test_file.parquet")

    @patch("pandas.read_parquet")
    @patch("ComStockProcessor.download_file")
    def test_process_metadata(self, mock_download_file, mock_read_parquet):
        mock_download_file.return_value = None
        data = {
            "in.county_name": ["OR, Multnomah County", "OR, Other County"],
            "in.comstock_building_type": ["MediumOffice", "OtherType"],
            "bldg_id": [1, 2],
        }
        df_test = pd.DataFrame(data)
        mock_read_parquet.return_value = df_test

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            processor = ComStockProcessor("OR", "Multnomah County", "MediumOffice", "0", tmp_path)
            meta_df = processor.process_metadata()

            self.assertEqual(len(meta_df), 1)
            self.assertEqual(meta_df.iloc[0]["bldg_id"], 1)

    @patch("pandas.read_parquet")
    @patch("ComStockProcessor.download_file")
    def test_process_building_time_series(self, mock_download_file, mock_read_parquet):
        mock_download_file.return_value = None
        mock_read_parquet.return_value = pd.DataFrame({"dummy_column": [1, 2, 3]})

        data = {
            "bldg_id": ["257118"],
        }
        meta_df = pd.DataFrame(data)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            processor = ComStockProcessor("OR", "Multnomah County", "MediumOffice", "0", tmp_path)
            processor.process_building_time_series(meta_df)

            output_csv = tmp_path / "257118-0.csv"
            self.assertTrue(os.path.exists(output_csv))
            df_test = pd.read_csv(output_csv)
            self.assertIn("dummy_column", df_test.columns)
            os.remove(output_csv)


if __name__ == "__main__":
    unittest.main()
