# utils/config_loader.py
import yaml

def load_config(path):
    """
    讀取 YAML 設定檔並回傳字典
    :param path: 設定檔路徑 (config.yaml)
    :return: dict 格式的設定內容
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
