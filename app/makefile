# 設定 Python 路徑
PYTHON := python

# 設定腳本路徑
TRUNCATE_SCRIPT := truncate_all_tables.py
LOAD_SCRIPT := load_sample_data.py

# 預設目標
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make truncate - truncate all tables"
	@echo "  make load     - load sample data"
	@echo "  make reset    - truncate all tables and load sample data"
	@echo "  make help     - show this help"

# truncate all tables
.PHONY: truncate
truncate:
	@echo "🗑️ truncate all tables..."
	@$(PYTHON) $(TRUNCATE_SCRIPT)

# 載入範例資料
.PHONY: load
load:
	@echo "📥 load sample data..."
	@$(PYTHON) $(LOAD_SCRIPT)

# 重置資料（清空後重新載入）
.PHONY: reset
reset:
	@echo "🔄 reset database..."
	@$(PYTHON) $(TRUNCATE_SCRIPT)
	@echo "\n"
	@$(PYTHON) $(LOAD_SCRIPT)
