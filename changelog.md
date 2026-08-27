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
    - TUrbine auto panel - 4
- Buttons to open panels have been removed to reduce clutter on the main page
- Placeholder help and about options
- Main menu added (thanks gemini for UI design I cant do CSS)
- Added debug panel with commands:
    - set_val {variable name} {value}
    - damage {value}
- Added log panel which logs events and their times (currently only logs some events)
- slight optimisation for log functions
- Demand generator added (still wip)
- Fixed annunciator class self.blink not activating when self.persistent is False
- Added automatic turbine control

## v0.4.1
- Added orange and red bars to the gauges to more clearly indicate the operating values
- Changed RPM (500RPM) to match that of a more realistic 12 pole generator
- Added spillway control
- Made water outflow relative to water level
- Added phone (functions missing)

## To do
- Update save system to support new variables
- Decrease gate delay when water fills the path (water hammer)
- Annunciators on other panels don't work when save file is loaded
- Add another window with grid conditions
- Add power/rpm mode for auto control
- Add grid frequency simulation
- Add graph system