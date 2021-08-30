# batch_vmt
batch .vmt generator (WIP)  

Uses [VTFLibWrapper by Ganonmaster](https://github.com/Ganonmaster/VTFLibWrapper),
which provides python bindings for [Nem's VTFLib](https://web.archive.org/web/20191229074421/http://nemesis.thewavelength.net/index.php?p=40)
(also used by the [SourceIO](https://github.com/REDxEYE/SourceIO/tree/master/source1/vtf/VTFWrapper) blender addon)  
See also: [VTFCmd](https://github.com/TitusStudiosMediaGroup/VTFcmd-Resources)

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
    - VTF reader (via VTFLibWrapper)
  * PyInstaller standalone .exe builds (coming soonTM)
