#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
import getopt
import datetime as dt
try:
    import pycalcal.pycalcal as pcc
except:
    import pycalcal as pcc
from collections import namedtuple

CDate = namedtuple('CDate', 'cycle, offset, month, leap, day')

def CDate_from_fixed(date):
    return CDate(*pcc.chinese_from_fixed(date))

_en_solterms = [
        "XH", "DH", "LC", "YS", "JZ", "CF", "QM", "GY",
        "LX", "XM", "MZ", "XZ", "XS", "DS", "LQ", "CS",
        "BL", "QF", "HL", "SJ", "LD", "XX", "DX", "DZ"]
_chs_solterms = [
        u'小寒', u'大寒', u'立春', u'雨水', u'惊蛰', u'春分', u'清明', u'谷雨',
        u'立夏', u'小满', u'芒种', u'夏至', u'小暑', u'大暑', u'立秋', u'处暑',
        u'白露', u'秋分', u'寒露', u'霜降', u'立冬', u'小雪', u'大雪', u'冬至']
_monnames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"]
_en_daynames = [
        "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"]
_chs_daynames = [
        u'Sun  日', u'Mon  一', u'Tue  二', u'Wed  三',
        u'Thu  四', u'Fri  五', u'Sat  六']
_daysinmonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_en_stems = [
        "Jia", "Yi", "Bing", "Ding", "Wu",
        "Ji", "Geng", "Xin", "Ren", "Gui"]
_chs_stems = [
        u'甲', u'乙', u'丙', u'丁', u'戊',
        u'己', u'庚', u'辛', u'壬', u'癸']
_en_branches = [
        "Zi", "Chou", "Yin", "Mou", "Chen", "Si",
        "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
_chs_branches = [
        u'子', u'丑', u'寅', u'卯', u'辰', u'巳',
        u'午', u'未', u'申', u'酉', u'戌', u'亥']
_en_miscchar = [
        ' ', '1', '2', '3', '4', '5',
        '6', '7', '8', '9', '10', '20',
        '1', 'R', 'Y', '', '', 'D', u'X', u',', u' ', u'S']
_chs_miscchar = [
        u'初', u'一', u'二', u'三', u'四', u'五',
        u'六', u'七', u'八', u'九', u'十', u'廿',
        u'正', u'闰', u'月', u'日', u'年', u'大', u'小', u'，', u'　', u'始']

def month_name(month, lang='en', miscchar=_en_miscchar):
    if lang == 'en':
        return month
    else:
        if month == 1:
            return miscchar[12]
        elif 1 < month <= 10:
            return miscchar[month]
        elif 10 < month <= 12:
            return miscchar[10] + miscchar[month - 10]
        else:
            raise Exception('Invalid month %s' % (month,))

def print_month(year, month, days, lang='en', enc='ascii', f=sys.stdout):
    if lang == 'en':
        solterms = _en_solterms
        daynames = _en_daynames
        stems    = _en_stems
        branches = _en_branches
        miscchar = _en_miscchar
        monhdpat0 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s)'
        monhdpat1 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d)'
        monhdpat2 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d, ' + \
                '%(aleap)s%(amonth)d%(alength)s S%(aday)d)'
        monhdpat3 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d, ' + \
                'Year %(astem)s%(abranch)s, Month ' + \
                '%(aleap)s%(amonth)d%(alength)s S%(aday)d)'
    else:
        solterms = _chs_solterms
        daynames = _chs_daynames
        stems    = _chs_stems
        branches = _chs_branches
        miscchar = _chs_miscchar
        monhdpat0 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s'
        monhdpat1 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始'
        monhdpat2 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始，' + \
                u'%(aleap)s%(amonth)s月%(alength)s%(aday)d日始'
        monhdpat3 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始，' + \
                u'%(astem)s%(abranch)s年' + \
                u'%(aleap)s%(amonth)s月%(alength)s%(aday)d日始'
    date = pcc.fixed_from_gregorian((year, month, 1))
    new_moon_date = pcc.chinese_new_moon_on_or_after(date)
    next_new_moon_date = pcc.chinese_new_moon_on_or_after(new_moon_date + 29)
    last_date = date + days - 1
    c_date = CDate_from_fixed(date)
    c_new_moon_date = CDate_from_fixed(new_moon_date)
    c_last_date = CDate_from_fixed(last_date)
    if new_moon_date <= last_date:
        if (c_new_moon_date.month, c_new_moon_date.leap) != (
                c_last_date.month, c_last_date.leap):
            assert last_date - c_last_date.day + 1 == next_new_moon_date
            next_next_nmd = pcc.chinese_new_moon_on_or_after(
                    next_new_moon_date + 29)
            if month == 1:
                assert c_new_moon_date.offset != c_last_date.offset
                monhdpat = monhdpat3
            else:
                assert c_new_moon_date.offset == c_last_date.offset
                monhdpat = monhdpat2
            monthhead = monhdpat % dict(
                    monname = _monnames[month - 1],
                    year = year,
                    stem = stems[(c_new_moon_date.offset - 1) % 10],
                    branch = branches[(c_new_moon_date.offset - 1) % 12],
                    month = month_name(c_new_moon_date.month, lang, miscchar),
                    leap = c_new_moon_date.leap and miscchar[13] or '',
                    length = miscchar[17 + int(
                        next_new_moon_date - new_moon_date == 29)],
                    day = new_moon_date - date + 1,
                    astem = stems[(c_last_date.offset - 1) % 10],
                    abranch = branches[(c_last_date.offset - 1) % 12],
                    amonth = month_name(c_last_date.month, lang, miscchar),
                    aleap = c_last_date.leap and miscchar[13] or '',
                    alength = miscchar[17 + int(
                        next_next_nmd - next_new_moon_date == 29)],
                    aday = next_new_moon_date - date + 1,
                    )
        else:
            monthhead = monhdpat1 % dict(
                    monname = _monnames[month - 1],
                    year = year,
                    stem = stems[(c_new_moon_date.offset - 1) % 10],
                    branch = branches[(c_new_moon_date.offset - 1) % 12],
                    month = month_name(c_new_moon_date.month, lang, miscchar),
                    leap = c_new_moon_date.leap and miscchar[13] or '',
                    length = miscchar[17 + int(
                        next_new_moon_date - new_moon_date == 29)],
                    day = new_moon_date - date + 1,
                    )
    else:
        last_new_moon_date = pcc.chinese_new_moon_before(date)
        assert month == 2
        monthhead = monhdpat0 % dict(
                monname = _monnames[month - 1],
                year = year,
                stem = stems[(c_date.offset - 1) % 10],
                branch = branches[(c_date.offset - 1) % 12],
                month = month_name(c_date.month, lang, miscchar),
                leap = c_date.leap and miscchar[13] or '',
                length = miscchar[17 + int(
                    new_moon_date - last_new_moon_date == 29)],
                )
    headlen = len(monthhead) + len(filter(lambda c: ord(c) > 0xFF, monthhead))
    print >> f, ' ' * max((68 - headlen) / 2, 0) + monthhead.encode(enc)

if __name__ == '__main__':
    name = os.path.basename(sys.argv[0])
    year, month = dt.date.today().timetuple()[:2]
    single = True
    try:
        opt, args = getopt.getopt(sys.argv[1:], 'gu')
        if len(args) == 1:
            year = int(args[0])
            single = False
        elif len(args) == 2:
            month, year = map(int, args)
        elif args:
            print '%s: Too many parameters.' % (name,)
            raise
        opt = dict(opt)
    except:
        print 'Usage: %s [-g] [-u] [[<month>] <year>].' % (name,)
        print '\t-g:\tGenerates simplified Chinese output.'
        print '\t-u:\tUses UTF-8 rather than GB for Chinese output.'
        sys.exit(1)
    if not 1 <= month <= 12:
        print '%s: Invalid month value: month 1-12.' % (name,)
        sys.exit(1)
    if not 1645 <= year <= 9999:
        print '%s: Invalid year value: year 1645-9999.' % (name,)
        sys.exit(1)
    if pcc.is_gregorian_leap_year(year):
        _daysinmonth[1] = 29
    if opt.has_key('-g'):
        lang = 'chs'
        if opt.has_key('-u'):
            enc = 'utf-8'
        else:
            enc = 'gb2312'
    elif opt.has_key('-u'):
        lang = 'chs'
        enc = 'utf-8'
    else:
        lang = 'en'
        enc = 'ascii'
    if single:
        print_month(year, month, _daysinmonth[month - 1], lang, enc)
    else:
        for i in xrange(12):
            print_month(year, i + 1, _daysinmonth[i], lang, enc)
