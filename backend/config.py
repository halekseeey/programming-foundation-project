import os
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Позже можно вынести в .env
    DATA_DIR = BASE_DIR / "data"
    DATA_RAW_DIR = DATA_DIR / "raw"
    DATA_CLEAN_DIR = DATA_DIR / "clean"
    CHARTS_DIR = DATA_DIR / "charts"
    
    # Файл Eurostat (ты его сам скачиваешь и кладёшь в backend/data/raw)
    NRG_IND_REN_FILE = DATA_RAW_DIR / "nrg_ind_ren.csv"
    
    @staticmethod
    def get_available_datasets() -> List[Dict[str, str]]:
        """Get list of available datasets from clean directory (merged dataset)"""
        datasets = []
        clean_dir = Config.DATA_CLEAN_DIR
        
        if not clean_dir.exists():
            return datasets
        
        # Check for merged dataset
        merged_file = clean_dir / "merged_dataset.csv"
        if merged_file.exists():
            datasets.append({
                "id": "merged_dataset",
                "name": "Merged Dataset",
                "filename": merged_file.name,
                "path": str(merged_file)
            })
        
        return datasets

def get_config():
    return Config()
