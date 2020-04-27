import json
import re
import math
from ..Script import Script

class ChangeTempEvery(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        # Create settings as an object
        settings = {
            "name": "Change temperature recurringly",
            "key": "ChangeTempEvery",
            "metadata": {},
            "version": 2,
            "settings": {
                "step_size": {
                    "label": "Step size",
                    "description": "The height steps at which to adjust nozzle temperature",
                    "unit": "mm",
                    "type": "float",
                    "minimum_value": 0,
                    "default_value": 5
                },
                "increase": {
                    "label": "Temperature increase",
                    "description": "Amount of degrees to adjust nozzle temperature by. Supports negative values to decrase temperature.",
                    "unit" : "C",
                    "type": "float",
                    "default_value": -5
                }
            }
        }

        json_settings = json.dumps(settings)
        return json_settings

    def execute(self, data):
        re_move = re.compile('^G(0|1)[^Z]+Z([0-9]+\\.?[0-9]*)')
        re_temp = re.compile('^M10(4|9)[^S]+S([0-9]+\\.?[0-9]*)')
        initialized_marker = ";LAYER_COUNT:"
        start_marker = ";LAYER:0"

        output = []
        initialized = False
        started = False
        finished = False
        initial_temp = 0.0
        current_temp = 0.0
        min_z = 0.0

        step_size = float(self.getSettingValueByKey("step_size"))
        increase = float(self.getSettingValueByKey("increase"))

        for layer in data:
            output_layer = ""
            for line in layer.split("\n"):
                # always output the current line
                output_layer += "%s\n" % line

                if initialized_marker in line:
                    initialized = True
                elif start_marker in line:
                    started = True
                else:
                    temp_match = re_temp.search(line)
                    if temp_match is not None:
                        initial_temp = float(temp_match.groups()[1])
                        current_temp = initial_temp

                if started and initial_temp == 0:
                    finished = True

                if line.startswith(";") or not initialized or finished:
                    continue

                move_match = re_move.search(line)
                if move_match is not None:
                    # read z position
                    new_z = float(move_match.groups()[1])

                    # still below layer0 -> printing raft, take it's top as base line
                    if not started:
                        min_z = new_z
                    
                    # calculate expected temperature
                    new_temp = get_temp(initial_temp, new_z - min_z, step_size, increase)
                    if new_temp != current_temp:
                        # is different than current, insert change command
                        current_temp = new_temp
                        output_layer += "M104 S%s ; inserted by ChangeTempEvery script\n" % int(current_temp)

            output.append(output_layer)

        return output


def get_temp(initial_temp, height, step_size, increase):
    step = math.floor(height / step_size)
    return step * increase + initial_temp
