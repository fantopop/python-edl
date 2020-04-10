import pandas as pd
from pandas.api.extensions import ExtensionDtype, register_extension_dtype

from typing import Type
from timecode import Timecode
from edl import Parser
import re


str_type = str
valid_frame_rates = [
    '23.976',
    '23.98',
    '24',
    '25',
    '29.97',
    '30',
    '50',
    '59.94',
    '60'
]


@register_extension_dtype
class PandasTimecode(ExtensionDtype):
    name = 'timecode'
    type: Type[Timecode] = Timecode
    _frame_rate = '25'

    def __init__(self, timecode: Timecode):
        self._timecode = timecode

    @property
    def timecode(self) -> Timecode:
        return self._timecode

    @property
    def framerate(self):
        return self.timecode.framerate

    @classmethod
    def set_frame_rate(cls, new_frame_rate):
        cls.validate_frame_rate(new_frame_rate)
        cls._frame_rate = new_frame_rate

    @staticmethod
    def validate_frame_rate(frame_rate):
        if frame_rate not in valid_frame_rates:
            raise TypeError(
                f'Expects a value from {str(valid_frame_rates)}, got {frame_rate}'
            )

    @staticmethod
    def validate_string(string):
        # check gor string type
        if type(string) != str_type:
            raise TypeError(f'Expects a string, got {type(string).__name__}')

        # check for correct pattern
        pattern = r'(\d\d):(\d\d):(\d\d)[:;\.](\d+)'
        match = re.search(pattern, string)
        if not match:
            raise TypeError(f'Incorrect Timecode string: {string}')

    @classmethod
    def construct_from_string(cls, string: str_type) -> 'PandasTimecode':
        cls.validate_string(string)
        timecode = Timecode(cls._frame_rate, string)
        return cls(timecode)


if __name__ == '__main__':
    parser = Parser('24')
    edl_path = '/Users/fantopop/GitHub/python-edl/tests/test_data/test_24.edl'
    with open(edl_path) as f:
        edl = parser.parse(f)

    e1 = edl.events[0]
    e2 = edl.events[1]

    e = [[e1.num, e1.reel, e1.track, e1.rec_start_tc, e1.rec_end_tc]]
    columns = ['num', 'reel', 'track', ['rec_start_tc'], ['rec_end_tc ']]
    dtypes = {
        'num': str_type,
        'reel': str_type,
        'track': str_type,
        'rec_start_tc': PandasTimecode,
        'rec_end_tc': PandasTimecode,
    }
    df = pd.DataFrame(data=e, columns=columns, dtype=dtypes)
