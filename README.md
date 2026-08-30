# Stay-Civilised

[![Trello](https://img.shields.io/badge/trello-8A2BE2)](https://trello.com/w/stayciviliseddev)

<img width="976" height="1104" alt="logo" src="https://github.com/user-attachments/assets/f66ac053-5f1c-453e-a524-373f0d3fc5fc" />

## Cloud save
1. Create an account on [this website](https://positron.my.id/stay-civilised)
2. Copy the token generated
3. Launch stay civilised and click on the `CLOUD SAVE` button on the main menu
4. Paste the token and upload save files
The menu does not automatically refreash. To see changes or load save files, press the `REFREASH` button.

## Quickstart (Windows)
**Clone repo**

Requires git installed [download](https://git-scm.com/install/)
```cmd
git clone https://github.com/wh4r/Stay-Civilised
cd Stay-Civilised
```

**Create virtual environment**
```cmd
py -m venv venv
```

**Install libraries**
```cmd
pip install -r requirements.txt
```

**Run main_menu.py**
```cmd
py main_menu.py
```
`py` may be `python` or `python3` on your computer.

Programmed and tested on python 3.14.3 avaialble [here](https://www.python.org/downloads/release/python-3143/)

## Installing SSL root certificate on apple devices
**This step must be done to use cloud saves**
Python does not create root certificates by default. To create a root certificate, navigate to the directory of the python version used. The python version can be checked using `python --version` in terminal. The directory will be `Applications/Python [version]`. Inside the folder, run `Install Certificates.command` and it will automatically install the root certificate.

## 🗺️ Roadmap

| Version | Feature | Status | Priority |
| :--- | :--- | :---: | :---: |
| **v0.2.0-demo** | Rewrite and panel demo | ✅ Live | High |
| **v0.3.0-demo** | Panel functionality | ✅ Live | High |
| **v0.4.0-demo** | Automatic turbine control | ✅ Live | Medium |
| **v1.0.0-alpha** | Spillway, demand, phone | 🏗️ In dev | High |
| **v1.1.0-alpha** | Maintenance | ⏳ Planned | High |

Versions are MAJOR.MINOR.PATCH-STAGE
