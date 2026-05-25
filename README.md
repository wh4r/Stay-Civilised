# Stay-Civilised

[![Trello](https://img.shields.io/badge/trello-8A2BE2)](https://trello.com/w/stayciviliseddev)

## Quickstart (Windows)
**Clone repo**
```cmd
git clone https://github.com/wh4r/Stay-Civilised
```

**Create virtual environment**
```cmd
py -m venv venv
```

**Install libraries**
```cmd
pip install -r requirements.txt
```

**Run simulator.py**
```cmd
cd "Hydro 1"
py simulator.py
```
`py` may be `python` or `python3` on your computer.

Programmed and tested on python 3.14.3 avaialble [here](https://www.python.org/downloads/release/python-3143/)

## 🗺️ Roadmap

| Version | Feature | Status | Priority |
| :--- | :--- | :---: | :---: |
| **v0.2.0** | Rewrite and panel demo | ✅ Live | High |
| **v0.2.1** | Panel functionality | 🏗️ Dev | High |
| **v0.2.2** | Optimisations | ⏳ Planned | Medium |
| **v0.2.3** | Automatic turbine control | ⏳ Planned | Low |
| **v0.3.0** | Spillway, demand, maintenance | ⏳ Planned | High |

## v0.2.0 Changelog

This is the largest update so far. Most of the physics has been moved to calculation.py and is run in simulator.py as self.engine. Excitation should work now (i think?). Hydraulics and electrical panels have been added and can be opened and closed via the buttons on the main panel. The hydraulics panel somewhat works and the electrical panel is only a proof of concept as of now. Expect these panels to be fully functional in v0.2.1. After 0.2.1, 0.2.2 will provide optimisations to remove redundant checks and calculations.

The old code is still available on the `0.1_before_rewrite` branch.

(thanks chatgpt for fixing my absolutely horrible naming scheme)