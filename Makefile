# ── Essential Model Documentation ────────────────────────────────────────────
# Makefile for common MkDocs tasks.
# All commands run from the repo root; mkdocs.yml lives in src/mkdocs/.

MKDOCS_CONFIG := src/mkdocs/mkdocs.yml
BUILD_DIR     := build
DOCS_DIR      := docs
PORT          ?= 8000
ADDR          := 127.0.0.1:$(PORT)

.PHONY: build serve dev clean install help

help:
	@echo ""
	@echo "  make install  Install Python dependencies from src/mkdocs/requirements.txt"
	@echo "  make build    Build the static site -> $(BUILD_DIR)/"
	@echo "  make dev      Serve with live-reload + open browser (http://$(ADDR))"
	@echo "  make serve    Serve locally with live-reload (http://$(ADDR))"
	@echo "                override the port with e.g. make serve PORT=7654"
	@echo "  make clean    Remove the build directory"
	@echo ""

install:
	pip install -r src/mkdocs/requirements.txt

build:
	mkdocs build --config-file $(MKDOCS_CONFIG)

serve:
	pkill -f "mkdocs serve"; mkdocs serve --config-file $(MKDOCS_CONFIG) --dev-addr $(ADDR)

dev:
	mkdocs serve --config-file $(MKDOCS_CONFIG) --dev-addr $(ADDR) & sleep 2 && open -a "Google Chrome" http://$(ADDR)/

clean:
	rm -rf $(BUILD_DIR)
