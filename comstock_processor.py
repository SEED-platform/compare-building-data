"""
@author: nllong (adapted from jho)
"""

import os
from pathlib import Path

import pandas as pd

# import pyarrow because it is used in parquet. Do not remove.
import pyarrow as pa  # noqa: F401
import requests
from pandas import DataFrame


class ComStockProcessor:
    def __init__(self, state: str, county_name: str, building_type: str, upgrade: str, base_dir: Path) -> None:
        self.state = state
        self.county_name = county_name
        self.building_type = building_type
        self.upgrade = upgrade
        self.base_dir = base_dir

        if not self.base_dir.exists():
            self.base_dir.mkdir()

        # data sets URL are here
        self.base_url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2023/comstock_amy2018_release_2/"
        # self.base_url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2024/comstock_amy2018_release_1/"
        self.metadata_url = self.base_url + "metadata/baseline.parquet"
        os.chdir(self.base_dir)

    def download_file(self, url: str, save_path: Path) -> None:
        response = requests.get(url, timeout=300)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
        else:
            print(f"Failed to download file: {url}")

    def process_metadata(self, save_dir: Path) -> DataFrame:
        self.download_file(self.metadata_url, save_dir / "comstock_metadata.parquet")
        meta_df = pd.read_parquet(save_dir / "comstock_metadata.parquet")
        meta_df = meta_df.reset_index(drop=False)

        lookup_county = f"{self.state}, {self.county_name}"
        if self.building_type != "All":
            if self.county_name != "All":
                meta_df = meta_df[
                    (meta_df["in.county_name"] == lookup_county) & (meta_df["in.comstock_building_type"] == self.building_type)
                ]
            else:
                meta_df = meta_df[meta_df["in.comstock_building_type"] == self.building_type]
        elif self.county_name != "All":
            meta_df = meta_df[meta_df["in.county_name"] == lookup_county]

        output_csv = save_dir / f"{self.state}-{self.county_name}-{self.building_type}-{self.upgrade}-selected_metadata.csv"
        meta_df.to_csv(output_csv, index=False)
        return meta_df

    def process_building_time_series(self, meta_df: DataFrame, save_dir: Path) -> None:
        for index, row in meta_df.iterrows():
            building_id = str(row["bldg_id"])
            print(f"Now Processing {building_id}")
            building_time_series_file = f"{self.base_url}timeseries_individual_buildings/by_state/upgrade={self.upgrade}/state={self.state}/{building_id}-{self.upgrade}.parquet"
            save_path = self.base_dir / f"{building_id}-{self.upgrade}.parquet"
            self.download_file(building_time_series_file, save_path)

            tdf = pd.read_parquet(save_path)
            tdf.to_csv(save_dir / f"{building_id}-{self.upgrade}.csv", index=False)
        print("Finished")


def main() -> None:
    # Settings for modification
    state = "All"
    county_name = "All"
    building_type = "All"
    upgrade = "0"

    save_dir = Path().resolve() / "datasets" / "comstock"
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)

    processor = ComStockProcessor(state, county_name, building_type, upgrade, save_dir)
    processor.process_metadata(save_dir=save_dir)

    # Do not pull down time series data, this would take forever :)
    # if needed, then assign the method process_metadata to a variable
    # meta_df = processor.process_metadata(save_dir=save_dir)
    # processor.process_building_time_series(meta_df, save_dir=save_dir)


if __name__ == "__main__":
    main()
