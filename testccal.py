#!/usr/bin/env python
import pyccal

assert __name__ == '__main__'

lcd = None
for year in xrange(1645, 7001):
    if pyccal.pcc.is_gregorian_leap_year(year):
        pyccal._daysinmonth[1] = 29
    else:
        pyccal._daysinmonth[1] = 28
    for i in xrange(12):
        lcd = pyccal.print_month(year, i + 1, pyccal._daysinmonth[i], 'chs', 'utf-8', lcd)
