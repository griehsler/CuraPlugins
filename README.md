# CuraPlugins
## Scripts
### Installation
Custom scripts can be added to Cura by copying them to the user scripts folder.
* Windows: `C:\Users\<user>\AppData\Roaming\cura\<version>\scripts`
* Linux: `~/.local/share/cura/<version>/scripts`
* macOS: `/Users/<user>/Library/Application\ Support/cura/<version>/scripts`
### ChangeTempEvery.py
A post processing script to iteratively adjust nozzle temperature. Practical for slicing temperature towers.

The printing temperature defined in the slicing settings will be taken as a basis. 
Then it will be adjusted as defined by 2 settings:
* Step size: Height intervals at which to perform temperature change. E.g. 5mm to let nozzle temperature change every 5mm.
* Temperature increase: The temperature adjustment to be performed at every step. E.g. 10 to let the temperature be increased by 10°. This settings accepts negative values, too, to let the temperature be decreased.

Example configuration:
Printing temperature = 220, Step size = 10, Temperature increase= -10, Total model height = 40mm
* the first 10mm will be printed at 220° 
* the second 10mm will be printed at 210° 
* the third 10mm will be printed at 200° 
* the last 10mm will be printed at 190° 
### RampFan.py
A post processing script to replace part cooling fan ramp up logic.

Default Cura fan control increases fan speed upon layer change. That might be unnessary slow on large models and dangerously quick on small models. _Too steep fan ramp up may cause the fan dropping down effective nozzle temperature too quick for the heater control to react accordingly, ultimately running into thermal runaway detection and emergency shutdown._ 

This script will increase fan speed progressively by overall extrusion length. This way print progress is measured in a more fine grained way than by layer changes. Large models will have fan speed changes within the same layer while small models will have speed hops only after a reasonable time, even if having progressed several layers meanwhile.

Currently these speed control profiles are supported:
* linear: speed increases are distributed evenly from start to target distance
* sigmoid: speed increases follow a [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function), yielding in soft ramp up, steep increase and soft approach to final speed
