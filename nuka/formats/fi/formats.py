# -*- encoding: utf-8 -*-
# This file is distributed under the same license as the Django package.
#
from __future__ import unicode_literals

# The *_FORMAT strings use the Django date format syntax,
# see http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'j. E Y'
TIME_FORMAT = 'G.i.s'
DATETIME_FORMAT = r'j. E Y \k\e\l\l\o G.i.s'
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'j. F'
SHORT_DATE_FORMAT = 'j.n.Y'
SHORT_DATETIME_FORMAT = 'j.n.Y \k\l\o G.i'
# FIRST_DAY_OF_WEEK =

# The *_INPUT_FORMATS strings use the Python strftime format syntax,
# see http://docs.python.org/library/datetime.html#strftime-strptime-behavior
# DATE_INPUT_FORMATS =
# TIME_INPUT_FORMATS =
# DATETIME_INPUT_FORMATS =
DATE_INPUT_FORMATS = (
    '%d.%m.%Y',
)
DATETIME_INPUT_FORMATS = (
    '%d.%m.%Y %H.%M',
    '%d.%m.%Y %H.%M.%S',
    '%d.%m.%Y %H:%M',
    '%d.%m.%Y %H:%M:%S',
)
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = ' '  # Non-breaking space
NUMBER_GROUPING = 3
