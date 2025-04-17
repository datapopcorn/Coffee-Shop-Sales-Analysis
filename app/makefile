# 設定 Python 路徑
PYTHON := python

# 設定腳本路徑
TRUNCATE_SCRIPT := truncate_all_tables.py
LOAD_SCRIPT := load_sample_data.py

# 預設目標
.PHONY: help
help:
	@echo "可用的指令："
	@echo "  make truncate  - 清空所有資料表"
	@echo "  make load     - 載入範例資料"
	@echo "  make reset    - 清空所有資料表並重新載入範例資料"
	@echo "  make help     - 顯示這個說明"

# 清空所有資料表
.PHONY: truncate
truncate:
	@echo "🗑️ 清空所有資料表..."
	@$(PYTHON) $(TRUNCATE_SCRIPT)

# 載入範例資料
.PHONY: load
load:
	@echo "📥 載入範例資料..."
	@$(PYTHON) $(LOAD_SCRIPT)

# 重置資料（清空後重新載入）
.PHONY: reset
reset:
	@echo "🔄 重置資料庫..."
	@$(PYTHON) $(TRUNCATE_SCRIPT)
	@echo "\n"
	@$(PYTHON) $(LOAD_SCRIPT)
