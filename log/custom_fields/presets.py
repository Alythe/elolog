import log.models
from types import FieldTypes, FIELD_TYPE_CHOICES
import json
import sys

__PRESET_DATA__ = None

def get_preset_data():
  global __PRESET_DATA__

  if __PRESET_DATA__ == None:
    stream = open("presets.json", "r")
    __PRESET_DATA__ = json.load(stream)
    stream.close()

  return __PRESET_DATA__

def initialize_preset(log_object, preset):
  print(preset)
  for field in preset:
    name = field
    order = preset[field]["order"]
    type = preset[field]["type"]

    for t in FIELD_TYPE_CHOICES:
      if t[1] == type:
        field = log.models.LogCustomField(log=log_object, name=name, order=order, type=t[0])
        field.save()
    
