# ── Essential Model Documentation ────────────────────────────────────────────
# Makefile for common MkDocs tasks.
# All commands run from the repo root; mkdocs.yml lives in src/mkdocs/.

MKDOCS_CONFIG := src/mkdocs/mkdocs.yml
BUILD_DIR     := build
DOCS_DIR      := docs

.PHONY: build serve clean install help

help:
	@echo ""
	@echo "  make install  Install Python dependencies from src/mkdocs/requirements.txt"
	@echo "  make build    Build the static site -> $(BUILD_DIR)/"
	@echo "  make serve    Serve locally with live-reload (http://127.0.0.1:8000)"
	@echo "  make clean    Remove the build directory"
	@echo ""

install:
	pip install -r src/mkdocs/requirements.txt

build:
	mkdocs build --config-file $(MKDOCS_CONFIG)

serve:
	mkdocs serve --config-file $(MKDOCS_CONFIG)

clean:
	rm -rf $(BUILD_DIR)
