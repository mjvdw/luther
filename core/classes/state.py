import json
import pandas as pd
import inspect

from core.classes.srzones.zone import Zone
from core.classes.srzones.line import Line
from core.classes.database import Database


class State(object):
    def __init__(self):
        self.new_state = {
            "support": None,
            "resistance": None
        }

        state_data = self._read_from_state_file()
        if not state_data:
            self._write_to_state_file(self.new_state)

    @property
    def support(self) -> Zone:
        support_data = self._read_from_state_file()["support"]
        coords = support_data["line_coords"]
        width = support_data["width"]
        support_line = Line(coords=coords)
        support_zone = Zone(line=support_line, width=width)
        return support_zone

    @support.setter
    def support(self, new_support_zone: Zone):
        support_coords = new_support_zone.line.coords[-2:]
        zone_width = new_support_zone.width
        new_value = {
            "line_coords": support_coords,
            "width": zone_width
        }
        self._set_property(value=new_value, key="support")

    @property
    def resistance(self) -> Zone:
        resistance_data = self._read_from_state_file()["resistance"]
        coords = resistance_data["line_coords"]
        width = resistance_data["width"]
        resistance_line = Line(coords=coords)
        resistance_zone = Zone(line=resistance_line, width=width)
        return resistance_zone

    @resistance.setter
    def resistance(self, new_resistance_zone: Zone):
        resistance_coords = new_resistance_zone.line.coords[-2:]
        zone_width = new_resistance_zone.width
        new_value = {
            "line_coords": resistance_coords,
            "width": zone_width
        }
        self._set_property(value=new_value, key="resistance")

    @staticmethod
    def _read_from_state_file():
        try:
            with open(Database.STATE_PATH, 'r') as state_file:
                state_data = state_file.read()
                data = json.loads(state_data)
                return data
        except ValueError:
            return None

    @staticmethod
    def _write_to_state_file(new_data):
        with open(Database.STATE_PATH, 'w') as state_file:
            json.dump(new_data, state_file)

    @classmethod
    def _set_property(cls, value, key):
        if inspect.isclass(value):
            data = vars(value)
        else:
            data = value

        state_data = cls._read_from_state_file()
        state_data[key] = data

        cls._write_to_state_file(state_data)
