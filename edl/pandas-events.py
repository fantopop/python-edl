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
    kind: str_type ='O'
    name = 'timecode'
    type: Type[Timecode] = Timecode
    _frame_rate = '25'

    def __init__(self, timecode: Timecode):
        self._timecode = timecode

    def __str__(self) -> str_type:
        return self.name

    def __repr__(self) -> str_type:
        return str(self)

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

    df = pd.DataFrame({
        'num': pd.Series([], dtype=str_type),
        'reel': pd.Series([], dtype=str_type),
        'track': pd.Series([], dtype=str_type),
        'rec_start_tc': pd.Series([], dtype=PandasTimecode),
        'rec_end_tc': pd.Series([], dtype=PandasTimecode),
    })

    for event in edl.events:
        row = [
            event.num,
            event.reel,
            event.track,
            event.rec_start_tc,
            event.rec_end_tc
        ]
        df.loc[len(df)] = row
    print(df)
    print(df.rec_start_tc + 10)
