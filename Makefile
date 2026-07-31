.DEFAULT_GOAL := verify
PYTHON ?= python3

.PHONY: test lint validate-examples package-smoke check-links verify

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m compileall -q scripts tests
	$(PYTHON) -m json.tool schemas/review-verdict.schema.json > /dev/null

validate-examples:
	$(PYTHON) scripts/validate_contract.py examples/high-risk-migration/contract.json

package-smoke:
	$(PYTHON) -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/adf-wheel-smoke .
	rm -rf /tmp/adf-wheel-smoke

check-links:
	$(PYTHON) scripts/check_links.py

verify: test lint validate-examples package-smoke check-links
