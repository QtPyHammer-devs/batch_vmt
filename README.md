# batch_vmt
batch .vmt generator (WIP)

## Installation
Clone this repo:  

```
git clone https://github.com/QtPyHammer-devs/batch_vmt.git
```  

Install dependencies with pip

```
py -3.9 -m venv venv
venv/scripts/activate
python -m pip --upgrade pip
python -m pip install -r requirements.txt
```

Run the Gooey GUI
```
python batch_vmt.py
```

## Not Yet Implemented
  * Metadata Parsing (Use --template mode instead!)
    - VTF reader (will copy over the QtPyHammer vtf classes later)
  * PyInstaller standalone .exe builds (coming soonTM)