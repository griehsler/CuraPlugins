# CuraPlugins
## Scripts
### Installation
Custom scripts can be added to Cura by copying them to the user scripts folder.
* Windows: `C:\Users\<user>\AppData\Roaming\cura\<version>\scripts`
* Linux: `~/.local/share/cura/<version>/scripts`
* macOS: `/Users/<user>/Library/Application\ Support/cura/<version>/scripts`
### RampFan.py
A post processing script to replace part cooling fan ramp up logic.

Default Cura fan control increases fan speed upon layer change. That might be unnessary slow on large models and dangerously quick on small models. _Too steep fan ramp up may cause the fan dropping down effective nozzle temperature too quick for the heater control to react accordingly, ultimately running into thermal runaway detection and emergency shutdown._ 

This script will increase fan speed progressively by overall extrusion length. This way print progress is measured in a more fine grained way than by layer changes. Large models will have fan speed changes within the same layer while small models will have speed hops only after a reasonable time, even if having progressed several layers meanwhile.

Currently these speed control profiles are supported:
* linear: speed increases are distributed evenly from start to target distance
* sigmoid: speed increases follow a [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function), yielding in soft ramp up, steep increase and soft approach to final speed
