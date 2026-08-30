## White/black box testing
White box testing has been used throughout the development process (every new function is tested after writing).For black box testing, there aren't really values to test but conditions (e.g. damaged turbine, extremely high rpm).
There are way too many parameters and results to document so here are a few of the more notable ones (in some sort of pseudopython).

Almost all syntax errors are caused by VS code not displaying variables that have been passed through 2 files. The engine from calculation.py is initialised in simulator.py where it is used to initialise the turbine panel class. VSC isn't smart enough to highlight or suggest variables from engine.py so typos cause crahes when the corrosponding window, button, etc. is used. Testing for these errors is difficult since these errors don't cause crashes untill the line of code is run.

```python
def sync:
    ...
    if phase_difference <= 3 and phase_difference >= 357 and ... :
        self.damage += ...
    ...
```
This results in the turbine always taking damage no matter how perfect the sync is. I assumed the phase difference worked in a circle with 1 coming after 359. During both white and black box testing, I failed to find the problem for way too long untill Harry noticed that these statements contradicted each other.

The original code for sounds used multiple threads and a queue. Soudns would be added to the queue, and played in quick succession (so it seems simultaneous). However, when a soudn fails to play, the code attempts to play it again. When the number of sounds queued exceeded the max number of threads, it would cause the program to crash since it tries to play the sound infinite times. The new soudn system takes all the fequencies playing, adds them together, then plays this new sound instead of the previous sound, fixing the crash and making the code significantly faster to execute.

When the code was first written, it was in 1 massive file. Without thinking about the varaible names, the different timed loops were named:
| Time between executions | Name |
| --- | --- |
| 50ms | update_simulation |
| 100ms | sim_loop_slow_main |
| 200ms | loop_1s |
| 500ms | blink_alarms |
| 1s | sim_loop_slow |
| 5s | update_water_inflow |

These horrible names have lead to many functions being placed in the wrong loop (especially the 1s loop that's actaully 200ms). These still haven't been changed cause it might break something else, following one of the rules of programming: if it isn't broken, dont touch it.

However, this isn't the end of the horrible names. Instead of naming the variables for the hydraulics system with reasonable names, I decided to name them:
```python
        self.pump1_state = 0  # 0: OFF, 1: STARTING, 2: RUNNING
        self.pump2_state = 0
        self.pump1_timer = 0.0
        self.pump2_timer = 0.0
        self.pump1_flow = 0.0
        self.pump2_flow = 0.0
        self.pump_selector = 1  # 1 or 2
        self.fan1_state = 0  # 0: OFF, 1: STARTING, 2: RUNNING
        self.fan2_state = 0
        self.fan1_timer = 0.0
        self.fan2_timer = 0.0
        self.pre1_on = False
        self.pre2_on = False
```
With no mention of hydraulics, these variables are quite confusing.

Res. 2 press. was labelled Res. 1. press for awy too long when I copied the code and forgot to change the label.

The save and load functions didn't work on macos since it uses `/` for paths and not `\` for windows. This was an easy fix since the code only needs to check the OS used and uses paths with the corrosponsing character.

The self.blink line was added since the annunciators would not light up if persistent was set to False. The default value for blink is False so the flashing can work.
```python
    def set_state(self, active):
        ...
        if self.persistent:
            if active and not self.active:
                self.needs_ack = True
        else:
            self.blink = True if active else False
        ...
```

## Integration testing
When new panels are added:
- No way to open the panel
- Panel crashes upon interaction
- Forgetting to pass the `SimulationEngine` class to the class of the panel

```python
def sim_loop_slow_main(self):
    ...
    self.engine.update_time()
```
Forgetting to add the update time function to sim_loop_slow_main