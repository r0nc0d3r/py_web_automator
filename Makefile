VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

.PHONY: run clean

run: $(VENV)/bin/activate
	$(PYTHON) src/website1.py

gen_link:
	$(PYTHON) src/gen_link.py

save_cookie:
	$(PYTHON) src/save_cookie.py

lesson_dl:
	$(PYTHON) src/lesson_dl.py

scrape:
	$(PYTHON) src/scrape.py

run_web2:
	$(PYTHON) src/website2.py

run_web3:
	$(PYTHON) src/website3.py

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf $(VENV)