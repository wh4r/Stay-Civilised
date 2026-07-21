## v0.4.0
With the addition of sounds, images, multiple menus, and save files, pyinstaller can no longer create a functioning executable. Follow the instructions in the quickstart to download and run the program (requires git).
- Replaced functions with changing variables directly
- Actually fixed sync parameters (further testing required)
- Fixed Res. 2 press. previously labelled with 1
- Added option to specify decimal places in gauges (defaults to 1)
- Gate guage displays 3d.p.
- Added sensitive gate control
- Added turbine panel
    - Turbine controls moved to this panel
    - Added simplified lubrcation system
    - Moved bypass and drain to turbine panel
- Added options to top of window
    - Save - ctrl/cmd+S
    - Load - ctrl/cmd+O
    - Exit - ctrl/cmd+Q
    - About
    - Turbine panel - 1
    - Hydraulics panel - 2
    - ELectrical panel - 3
- Buttons to open panels have been removed to reduce clutter on the main page
- Placeholder help and about options
- Main menu added (thanks gemini for UI design I cant do CSS)
- Added debug panel with commands:
    - set_val {variable name} {value}
    - damage {value}
- Added log panel which logs events and their times (currently only logs some events)
- slight optimisation for log functions
- Demand generator added (still wip)

## To do
- Automatic turbine control