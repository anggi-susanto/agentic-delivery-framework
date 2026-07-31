.DEFAULT_GOAL := verify
PYTHON ?= python3

.PHONY: test lint validate-examples package-smoke check-links verify

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m compileall -q src scripts tests
	$(PYTHON) -m json.tool schemas/review-verdict.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/task-contract.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/evidence-plan.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/scope-handshake.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/review-record.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/finding-event.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/eval-run.schema.json > /dev/null
	$(PYTHON) -m json.tool schemas/eval-summary.schema.json > /dev/null
	PYTHONPATH=src $(PYTHON) -c 'import adf; print(adf.__version__)'
	PYTHONPATH=src $(PYTHON) -m unittest tests.test_ledger -v

validate-examples:
	@set -e; \
	for contract in examples/contracts/*.json; do \
		$(PYTHON) scripts/validate_contract.py "$$contract"; \
	done
	$(PYTHON) scripts/validate_contract.py examples/high-risk-migration/contract.json

package-smoke:
	$(PYTHON) -m pip wheel --no-deps --no-build-isolation --wheel-dir /tmp/adf-wheel-smoke .
	rm -rf /tmp/adf-wheel-smoke

check-links:
	$(PYTHON) scripts/check_links.py

verify: test lint validate-examples package-smoke check-links
