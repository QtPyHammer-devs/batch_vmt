py -3.9 -m venv venv
venv/scripts/activate
python -m pip --upgrade pip
python -m pip install -r requirements.txt
:: can folders be passed to the CLI script with a drag and drop?
:: e.g. `python batch_vmt.py %*` ?
python batch_vmt.py
deactivate
