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
    

def get_config():
    return Config()
