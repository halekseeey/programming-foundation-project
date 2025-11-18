import os
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Позже можно вынести в .env
    DATA_DIR = BASE_DIR / "data"
    # Файл Eurostat (ты его сам скачиваешь и кладёшь в backend/data)
    NRG_IND_REN_FILE = DATA_DIR / "nrg_ind_ren.csv"
    
    @staticmethod
    def get_available_datasets() -> List[Dict[str, str]]:
        """Get list of available datasets for merging (only nrg_bal and nrg_ind_ren)"""
        datasets = []
        data_dir = Config.DATA_DIR
        
        if not data_dir.exists():
            return datasets
        
        # Only allow these two datasets for merging
        allowed_datasets = ["nrg_bal", "nrg_ind_ren"]
        
        for dataset_id in allowed_datasets:
            file_path = data_dir / f"{dataset_id}.csv"
            if file_path.exists():
                datasets.append({
                    "id": dataset_id,
                    "name": dataset_id.replace("_", " ").title(),
                    "filename": file_path.name,
                    "path": str(file_path)
                })
        
        return datasets

def get_config():
    return Config()
