# ── Essential Model Documentation ────────────────────────────────────────────
# Builds the documentation site with Zensical. Run every command from the
# repository root. Config: zensical.toml. Output: build/.
#
# Zensical runs no MkDocs hooks or gen-files scripts, so `make build` runs the
# EMD steps around the Zensical build itself:
#   1. generate    docs/scripts/*.py write the generated data pages
#   2. site        zensical build
#   3. postbuild   strip number prefixes, build the sidebar from
#                  docs/nav_order.json and inject it into every page
# Because the sidebar is added after the build, `make serve` serves the
# finished build/ folder rather than Zensical's live preview.

ZENSICAL_CONFIG := zensical.toml
BUILD_DIR       := build
PORT            ?= 8000
ADDR            := 127.0.0.1:$(PORT)
PYTHON          ?= python3

.DEFAULT_GOAL := help
.PHONY: help install build build-fast generate site postbuild serve dev clean

help:
	@echo ""
	@echo "  make install     Install the dependencies (src/zensical/requirements.txt)"
	@echo "  make build       Generate the data pages, build with Zensical, add the sidebar -> $(BUILD_DIR)/"
	@echo "  make build-fast  The same without the data-page generators (for theme and text changes)"
	@echo "  make serve       Build, then serve $(BUILD_DIR)/ at http://$(ADDR)"
	@echo "  make dev         Build fast, serve, and open the browser"
	@echo "  make clean       Remove $(BUILD_DIR)/"
	@echo ""
	@echo "  Override the port:    make serve PORT=7654"
	@echo "  Override the Python:  make build PYTHON=python"
	@echo ""

install:
	$(PYTHON) -m pip install -r src/zensical/requirements.txt

build: clean generate site postbuild

build-fast: clean site postbuild

generate:
	$(PYTHON) src/mkdocs/hooks/run_scripts.py

site:
	zensical build -f $(ZENSICAL_CONFIG)

postbuild:
	$(PYTHON) src/zensical/post_build.py

serve: build
	$(PYTHON) -m http.server $(PORT) --bind 127.0.0.1 --directory $(BUILD_DIR)

dev: build-fast
	@( sleep 1 && $(PYTHON) -m webbrowser http://$(ADDR)/ >/dev/null 2>&1 ) &
	$(PYTHON) -m http.server $(PORT) --bind 127.0.0.1 --directory $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
