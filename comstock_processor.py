#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: nllong (adapted from jho)
"""

import pandas as pd
import requests
import os
from pathlib import Path
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
            
        self.base_url = "https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2023/comstock_amy2018_release_2/"
        self.metadata_url = self.base_url + "metadata/baseline.parquet"
        os.chdir(self.base_dir)

    def download_file(self, url: str, save_path: Path) -> None:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
        else:
            print(f"Failed to download file: {url}")

    def process_metadata(self) -> DataFrame:
        self.download_file(self.metadata_url, self.base_dir / "comstock_metadata.parquet")
        meta_df = pd.read_parquet(self.base_dir / "comstock_metadata.parquet")
        meta_df.reset_index(drop=False, inplace=True)
        
        lookup_county = f"{self.state}, {self.county_name}"
        meta_df = meta_df[
            (meta_df['in.county_name'] == lookup_county) &
            (meta_df['in.comstock_building_type'] == self.building_type)
        ]
        
        output_csv = self.base_dir / f"{self.state}-{self.county_name}-{self.building_type}-{self.upgrade}-selected_metadata.csv"
        meta_df.to_csv(output_csv, index=False)
        return meta_df

    def process_building_time_series(self, meta_df: DataFrame) -> None:
        for index, row in meta_df.iterrows():
            building_id = str(row['bldg_id'])
            print(f"Now Processing {building_id}")
            building_time_series_file = f"{self.base_url}timeseries_individual_buildings/by_state/upgrade={self.upgrade}/state={self.state}/{building_id}-{self.upgrade}.parquet"
            save_path = self.base_dir / f"{building_id}-{self.upgrade}.parquet"
            self.download_file(building_time_series_file, save_path)
            
            tdf = pd.read_parquet(save_path)
            tdf.to_csv(self.base_dir / f"{building_id}-{self.upgrade}.csv", index=False)
        print("Finished")

def main() -> None:
    # Settings for modification
    state = 'OR'
    county_name = 'Multnomah County'
    building_type = 'MediumOffice'
    upgrade = '0'
    # get the current working directory
    base_dir = Path(__file__).resolve().parent / 'ComStock'

    processor = ComStockProcessor(state, county_name, building_type, upgrade, base_dir)
    meta_df = processor.process_metadata()
    processor.process_building_time_series(meta_df)

if __name__ == "__main__":
    main()
