import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from cjworkbench.types import NumberFormatter  # internal API


def _format_number(series: pd.Series, format: str) -> pd.Series:
    # TODO make this use `ColumnType.NUMBER.format_series()` -- which already
    # does all this.
    #
    # assume Workbench gave us a valid format; otherwise ValueError seems
    # sensible
    formatter = NumberFormatter(format)
    ret = series.map(formatter.format, na_action='ignore')
    # Pandas will still think all-NA is number.
    if is_numeric_dtype(ret):
        ret = ret.astype(object)
    return ret


def _format_datetime(series: pd.Series, format: None) -> pd.Series:
    na = series.isna()
    ret = series.astype(str)
    ret[na] = np.nan
    return ret


def render(table, params, *, input_columns):
    # if no column has been selected, return table
    if not params['colnames']:
        return table

    columns = [input_columns[c] for c in params['colnames'].split(',')]

    # Format one column at a time, and modify the table in-place. That uses a
    # more reasonable amount of RAM than modifying every column at the same
    # time.
    for column in columns:
        if column.type == 'number':
            table[column.name] = _format_number(table[column.name],
                                                column.format)
        elif column.type == 'datetime':
            table[column.name] = _format_datetime(table[column.name],
                                                  column.format)
        # else it's text already (no-op)

    return table