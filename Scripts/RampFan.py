import json
import re
import math
from ..Script import Script

class RampFan(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        # Create settings as an object
        settings = {
            "name": "Ramp up part cooling fan",
            "key": "RampFan",
            "metadata": {},
            "version": 2,
            "settings": {
                "target_extrusion_length": {
                    "label": "Target Extrusion Length",
                    "description": "The extrusion length at which the final fan speed should be reached",
                    "unit": "mm",
                    "type": "int",
                    "minimum_value": "0",
                    "default_value": "100"
                },
                "fan_start": {
                    "label": "Fan start at",
                    "description": "Minimum useful fan speed (some fans don't really start spinning below a certain power level)",
                    "unit" : "%",
                    "type": "int",
                    "default_value": "10",
                    "minimum_value": "0",
                    "maximum_value": "100"
                },
                "fan_target": {
                    "label": "Fan target",
                    "description": "Fan speed to ramp up to",
                    "unit" : "%",
                    "type": "int",
                    "default_value": "100",
                    "minimum_value": "0",
                    "maximum_value": "100"
                },
                "fan_stepsize": {
                    "label": "Fan step size",
                    "description": "Allowed increases of fan speed",
                    "unit" : "%",
                    "type": "int",
                    "default_value": "5",
                    "minimum_value": "1",
                    "maximum_value": "100"
                },
                "mode": {
                    "label": "Ramp mode",
                    "description": "mathematical function for ramping",
                    "type": "enum",
                    "options": {"linear":"Linear","sigmoid":"Sigmoid (S-shape)"},
                    "default_value": "linear"
                }
            }
        }

        json_settings = json.dumps(settings)
        return json_settings

    def execute(self, data):
        #start_temp = self.getSettingValueByKey("start_temperature")

        re_extrude = re.compile('^G(0|1|2|3|5) .* E([0-9]+\\.?[0-9]*)')

        output = []
        started = False
        finished = False
        extrusion_length_abs = -1
        extrusion_length_rel = 0

        target_extrusion_length = int(self.getSettingValueByKey("target_extrusion_length"))
        fan_start = int(self.getSettingValueByKey("fan_start")) * 2.55
        fan_target = int(self.getSettingValueByKey("fan_target")) * 2.55
        fan_stepsize = int(self.getSettingValueByKey("fan_stepsize")) * 2.55
        mode = self.getSettingValueByKey("mode")

        for layer in data:
            output_layer = ""
            for line in layer.split("\n"):
    
                if "M106" in line:
                    output_layer += "; disabled by fan ramping ;"

                # always output the current line
                output_layer += "%s\n" % line

                if not started and "LAYER:1" in line:
                    started = True
                    current_fan = fan_start
                    if current_fan > 0:
                        output_layer += "%s\n" % get_fan_command(current_fan)

   
                if line.startswith(";") or not started or finished:
                    continue

                match = re_extrude.search(line)

                if match is not None:
                    # read e position
                    new_e = float(match.groups()[1])

                    if extrusion_length_abs == -1:
                        # first E value ever -> start position
                        extrusion_length_abs = new_e
                    else:
                        movement = new_e - extrusion_length_abs
                        if movement > 0: # ignore retractions
                            extrusion_length_abs = new_e
                            extrusion_length_rel += movement
                            length_progress = extrusion_length_rel / target_extrusion_length
                            new_fan = get_fan_value(length_progress, mode) * fan_target
                            if (new_fan > current_fan and (new_fan == fan_target or new_fan - current_fan > fan_stepsize)):
                                current_fan = new_fan
                                output_layer += "%s\n" % get_fan_command(current_fan)

                                if current_fan == fan_target:
                                    finished = True


            output.append(output_layer)

        return output


def get_fan_command(rate):
    return "M106 S%d ; fan ramping" % round(rate)

def get_fan_value(x, mode):
    if mode == "sigmoid":
        y = math.atan(x*5-2.45)/2.35 + 0.5
    else:
        y = x
    
    # trim the result down to 0 <= y <= 1
    return min(max(y, 0), 1)
