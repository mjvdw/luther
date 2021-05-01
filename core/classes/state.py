import json
import inspect

from core.classes.srzones.zone import Zone
from core.classes.srzones.line import Line
from core.classes.database import Database


class State(object):
    def __init__(self):
        """
        Object for handling the scripts state between websocket messages.
        """
        self.new_state = {
            "support": None,
            "resistance": None,
            "last_signal": None,
            "existing_position": None
        }

        state_data = self._read_from_state_file()
        if not state_data:
            self._write_to_state_file(self.new_state)

    @property
    def support(self):
        """
        Read parameters and reconstruct the support zone.
        :return: A Zone object representing the support level.
        """
        support_data = self._read_from_state_file()["support"]
        if support_data:
            coords = support_data["line_coords"]
            width = support_data["width"]
            support_line = Line(coords=coords)
            support_zone = Zone(line=support_line, width=width)
            return support_zone
        else:
            return None

    @support.setter
    def support(self, new_support_zone: Zone):
        """
        Write parameters to state.json file to reconstruct support zone.
        :param new_support_zone: Zone object for current support zone.
        """
        support_coords = new_support_zone.line.coords[-2:]
        zone_width = new_support_zone.width
        new_value = {
            "line_coords": support_coords,
            "width": zone_width
        }
        self._set_property(value=new_value, key="support")

    @property
    def resistance(self):
        """
        Read parameters and reconstruct the resistance zone.
        :return: A Zone object representing the resistance level.
        """
        resistance_data = self._read_from_state_file()["resistance"]
        if resistance_data:
            coords = resistance_data["line_coords"]
            width = resistance_data["width"]
            resistance_line = Line(coords=coords)
            resistance_zone = Zone(line=resistance_line, width=width)
            return resistance_zone
        else:
            return None

    @resistance.setter
    def resistance(self, new_resistance_zone: Zone):
        """
        Write parameters to state.json file to reconstruct resistance zone.
        :param new_resistance_zone: Zone object for current resistance zone.
        """
        resistance_coords = new_resistance_zone.line.coords[-2:]
        zone_width = new_resistance_zone.width
        new_value = {
            "line_coords": resistance_coords,
            "width": zone_width
        }
        self._set_property(value=new_value, key="resistance")

    @property
    def last_signal(self):
        """

        :return:
        """
        return self._read_from_state_file()["last_signal"]

    @last_signal.setter
    def last_signal(self, last_signal):
        """
    
        :param last_signal: 
        :return: 
        """
        self._set_property(value=last_signal, key="last_signal")

    @property
    def existing_position(self):
        """

        :return:
        """
        return self._read_from_state_file()["existing_position"]

    @existing_position.setter
    def existing_position(self, existing_position):
        """

        :param existing_position:
        :return:
        """
        self._set_property(value=existing_position, key="existing_position")

    @staticmethod
    def _read_from_state_file():
        """
        Helper method for getting data from state.json file.
        :return: a dictionary containing the state data.
        """
        try:
            with open(Database.STATE_PATH, 'r') as state_file:
                state_data = state_file.read()
                data = json.loads(state_data)
                return data
        except ValueError:
            return None

    @staticmethod
    def _write_to_state_file(new_data):
        """
        Helper method for writing data to state.json file.
        :param new_data: the new data to write.
        """
        with open(Database.STATE_PATH, 'w') as state_file:
            json.dump(new_data, state_file)

    @classmethod
    def _set_property(cls, value, key):
        """
        Helper method for setting properties by reference to the state.json file.
        :param value: the new value to set.
        :param key: the key to be used to select the correct part of the state.json file.
        """
        if inspect.isclass(value):
            data = vars(value)
        else:
            data = value

        state_data = cls._read_from_state_file()
        state_data[key] = data

        cls._write_to_state_file(state_data)

    @classmethod
    def reset(cls):
        """
        Helper method for resetting the state file to its beginning state.
        """
        state = cls()
        state._write_to_state_file(state.new_state)
