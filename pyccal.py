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
        "[XH]", "[DH]", "[LC]", "[YS]", "[JZ]", "[CF]", "[QM]", "[GY]",
        "[LX]", "[XM]", "[MZ]", "[XZ]", "[XS]", "[DS]", "[LQ]", "[CS]",
        "[BL]", "[QF]", "[HL]", "[SJ]", "[LD]", "[XX]", "[DX]", "[DZ]"]
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
        '1', 'R', 'Y', 'D', u'X', u'S']
_chs_miscchar = [
        u'初', u'一', u'二', u'三', u'四', u'五',
        u'六', u'七', u'八', u'九', u'十', u'廿',
        u'正', u'闰', u'月', u'大', u'小', u'始']

def month_name(c_date, lang='en', miscchar=_en_miscchar):
    if lang == 'en':
        return c_date.month
    else:
        if c_date.month == 1 and not c_date.leap:
            return miscchar[12]
        elif c_date.month <= 10:
            return miscchar[c_date.month]
        else:
            return miscchar[10] + miscchar[c_date.month - 10]

def day_name(day, lang='en', miscchar=_en_miscchar):
    if lang == 'en':
        return '[%2d]' % (day,)
    else:
        assert day > 0
        if day <= 10:
            return miscchar[0] + miscchar[day]
        elif day == 20 or day == 30:
            return miscchar[day / 10] + miscchar[10]
        else:
            a, b = divmod(day, 10)
            return miscchar[9 + a] + miscchar[b]

def print_month(year, month, days, lang='en', enc='ascii',
        last_c_date=None, ext={}, f=sys.stdout):
    if lang == 'en':
        solterms = _en_solterms
        daynames = _en_daynames
        stems    = _en_stems
        branches = _en_branches
        miscchar = _en_miscchar
        monhdfmt0 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s)'
        monhdfmt1 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d)'
        monhdfmt2 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d, ' + \
                '%(aleap)s%(amonth)d%(alength)s S%(aday)d)'
        monhdfmt3 = '%(monname)s %(year)d (Year %(stem)s%(branch)s, ' + \
                'Month %(leap)s%(month)d%(length)s S%(day)d, ' + \
                'Year %(astem)s%(abranch)s, Month ' + \
                '%(aleap)s%(amonth)d%(alength)s S%(aday)d)'
        dayowfmt = '%-10s'
    else:
        solterms = _chs_solterms
        daynames = _chs_daynames
        stems    = _chs_stems
        branches = _chs_branches
        miscchar = _chs_miscchar
        monhdfmt0 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s'
        monhdfmt1 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始'
        monhdfmt2 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始，' + \
                u'%(aleap)s%(amonth)s月%(alength)s%(aday)d日始'
        monhdfmt3 = u'%(monname)s %(year)d  %(stem)s%(branch)s年' + \
                u'%(leap)s%(month)s月%(length)s%(day)d日始，' + \
                u'%(astem)s%(abranch)s年' + \
                u'%(aleap)s%(amonth)s月%(alength)s%(aday)d日始'
        dayowfmt = '%s   '
    date = pcc.fixed_from_gregorian((year, month, 1))
    new_moon_date = pcc.chinese_new_moon_on_or_after(date)
    next_new_moon_date = pcc.chinese_new_moon_on_or_after(new_moon_date + 29)
    last_date = date + days - 1
    #c_date = CDate_from_fixed(date)
    #c_new_moon_date = CDate_from_fixed(new_moon_date)
    #c_last_date = CDate_from_fixed(last_date)
    minor_solterm_date = pcc.minor_solar_term_on_or_after(date)
    major_solterm_date = pcc.major_solar_term_on_or_after(date)
    minor_solterm_date, major_solterm_date = map(pcc.fixed_from_moment,
            (minor_solterm_date, major_solterm_date))
    if not last_c_date:
        c_date = CDate_from_fixed(date)
    else:
        if last_c_date.day < 29 or (last_c_date.day == 29
                and date != new_moon_date):
            c_date = CDate(last_c_date.offset, last_c_date.offset,
                    last_c_date.month, last_c_date.leap, last_c_date.day + 1)
        else:
            assert date == new_moon_date
            if last_c_date.month == 12:
                if last_c_date.offset == 60:
                    c_date = CDate(last_c_date.cycle + 1, 1, 1, False, 1)
                else:
                    c_date = CDate(last_c_date.cycle, last_c_date.offset + 1,
                            1, False, 1)
            else:
                c_date = CDate(last_c_date.cycle, last_c_date.offset,
                        last_c_date.month + 1, False, 1)
    if new_moon_date == date:
        c_new_moon_date = c_date
    elif (new_moon_date <= major_solterm_date
            or new_moon_date + 5 > last_date): # next major solterm 19~24-29~30
        if c_date.month == 12:
            if c_date.offset == 60:
                c_new_moon_date = CDate(c_date.cycle + 1, 1, 1, False, 1)
            else:
                c_new_moon_date = CDate(c_date.cycle, c_date.offset + 1,
                        1, False, 1)
        else:
            c_new_moon_date = CDate(c_date.cycle, c_date.offset,
                    c_date.month + 1, False, 1)
    else:
        c_new_moon_date = CDate_from_fixed(new_moon_date)
    if last_date >= new_moon_date:
        if last_date < next_new_moon_date:
            c_last_date = CDate(c_new_moon_date.cycle, c_new_moon_date.offset,
                    c_new_moon_date.month, c_new_moon_date.leap,
                    c_new_moon_date.day + last_date - new_moon_date)
        else:
            c_last_date = CDate_from_fixed(last_date)
    else:
        c_last_date = CDate(c_date.cycle, c_date.offset,
                c_date.month, c_date.leap, c_date.day + last_date - date)
    if new_moon_date <= last_date:
        if (c_new_moon_date.month, c_new_moon_date.leap) != (
                c_last_date.month, c_last_date.leap):
            assert last_date - c_last_date.day + 1 == next_new_moon_date
            next_next_nmd = pcc.chinese_new_moon_on_or_after(
                    next_new_moon_date + 29)
            if month == 1:
                assert c_new_moon_date.offset != c_last_date.offset
                monhdfmt = monhdfmt3
            else:
                assert c_new_moon_date.offset == c_last_date.offset
                monhdfmt = monhdfmt2
            monthhead = monhdfmt % dict(
                    monname = _monnames[month - 1],
                    year = year,
                    stem = stems[(c_new_moon_date.offset - 1) % 10],
                    branch = branches[(c_new_moon_date.offset - 1) % 12],
                    month = month_name(c_new_moon_date, lang, miscchar),
                    leap = c_new_moon_date.leap and miscchar[13] or '',
                    length = miscchar[15 + int(
                        next_new_moon_date - new_moon_date == 29)],
                    day = new_moon_date - date + 1,
                    astem = stems[(c_last_date.offset - 1) % 10],
                    abranch = branches[(c_last_date.offset - 1) % 12],
                    amonth = month_name(c_last_date, lang, miscchar),
                    aleap = c_last_date.leap and miscchar[13] or '',
                    alength = miscchar[15 + int(
                        next_next_nmd - next_new_moon_date == 29)],
                    aday = next_new_moon_date - date + 1,
                    )
        else:
            monthhead = monhdfmt1 % dict(
                    monname = _monnames[month - 1],
                    year = year,
                    stem = stems[(c_new_moon_date.offset - 1) % 10],
                    branch = branches[(c_new_moon_date.offset - 1) % 12],
                    month = month_name(c_new_moon_date, lang, miscchar),
                    leap = c_new_moon_date.leap and miscchar[13] or '',
                    length = miscchar[15 + int(
                        next_new_moon_date - new_moon_date == 29)],
                    day = new_moon_date - date + 1,
                    )
    else:
        #last_new_moon_date = pcc.chinese_new_moon_before(date)
        last_new_moon_date = date - c_date.day + 1
        assert month == 2
        monthhead = monhdfmt0 % dict(
                monname = _monnames[month - 1],
                year = year,
                stem = stems[(c_date.offset - 1) % 10],
                branch = branches[(c_date.offset - 1) % 12],
                month = month_name(c_date, lang, miscchar),
                leap = c_date.leap and miscchar[13] or '',
                length = miscchar[15 + int(
                    new_moon_date - last_new_moon_date == 29)],
                )
    headlen = len(monthhead) + len(filter(lambda c: ord(c) > 0xFF, monthhead))
    def println(s):
        print >> f, s.encode(enc)
    println(' ' * max((68 - headlen) / 2, 0) + monthhead)
    println(''.join([dayowfmt % (daynames[i],) for i in xrange(7)]))
    dofw = pcc.day_of_week_from_fixed(date)
    if dofw > 4 and days == 31 or dofw > 5 and days == 30:
        weeks = 6
    else:
        weeks = 5
    dcnt, ldcnt = 1, c_date.day
    sameday = False
    show = ext.get('show')
    if show:
        stem, branch = pcc.chinese_day_name(date)
        stem -= 1
        branch -= 1
    for w in xrange(weeks):
        ar = []
        br = []
        for i in xrange(7):
            if dcnt > days:
                break
            if w == 0 and i < dofw:
                ar.append('          ')
                br.append('          ')
                continue
            ar.append('%2d' % (dcnt,))
            if not sameday and (date != minor_solterm_date
                    and date != major_solterm_date
                    and date != new_moon_date):
                ar.append(' %s   ' % (day_name(ldcnt, lang, miscchar)))
            elif sameday or (date != minor_solterm_date
                    and date != major_solterm_date
                    and date == new_moon_date):
                s = month_name(c_new_moon_date, lang, miscchar)
                if type(s) == int:
                    ar.append(' [%2d]Y%s ' % (s,
                        c_new_moon_date.leap and miscchar[13] or ' '))
                else:
                    assert s
                    if c_new_moon_date.leap:
                        s = miscchar[13] + s
                    s += miscchar[14]
                    if len(s) == 2:
                        ar.append(' %s   ' % (s,))
                    elif len(s) == 3:
                        ar.append(' %s ' % (s,))
                    else:
                        ar.append(s)
                if sameday:
                    sameday = False
                elif next_new_moon_date <= last_date:
                    new_moon_date = next_new_moon_date
                    c_new_moon_date = c_last_date
                    ldcnt = 1
                else:
                    ldcnt = 1
            else:
                if date == new_moon_date:
                    sameday = True
                    ldcnt = 1
                    if next_new_moon_date <= last_date:
                        new_moon_date = next_new_moon_date
                        c_new_moon_date = c_last_date
                n = (month - 1) * 2
                if date == major_solterm_date:
                    n += 1
                ar.append(' %s   ' % (solterms[n],))
            if show:
                s = stems[stem] + branches[branch]
                x = len(filter(lambda c: ord(c) > 0xFF, s))
                br.append(s.center(10 - x)[:10])
                stem += 1
                if stem == 10:
                    stem = 0
                branch += 1
                if branch == 12:
                    branch = 0
            date += 1
            dcnt += 1
            ldcnt += 1
        println(''.join(ar))
        if show:
            println(''.join(br))
    return c_last_date

if __name__ == '__main__':
    name = os.path.basename(sys.argv[0])
    year, month = dt.date.today().timetuple()[:2]
    single = True
    try:
        opt, args = getopt.getopt(sys.argv[1:], 'gusla:d:c')
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
        print 'Usage: %s [-g] [-u] [-s|-l|-a|-d] [-c] [[<month>] <year>].' % (
                name,)
        print '\t-g:\tGenerates simplified Chinese output.'
        print '\t-u:\tUses UTF-8 rather than GB for Chinese output.'
        print '\t-s:\tShow lines for daily sexagesimal names and misc terms.'
        print '\t-c:\tUse BenCaoGangMu rules for phenology of plum-rains'
        print('\t\t ShenShuJing rules: RuMei on 1st Bing day after MZ, '
                'ChuMei on 1st Wei day after XS (default)')
        print('\t\t BenCaoGangMu rules: RuMei on 1st Ren day after MZ, '
                'ChuMei on 1st Ren day after XS')
        print '\t-l:\tList of registered anniversaries of birth / death.'
        print('\t-a:\tAdd anniversary. Syntax: -a <ID_en> <ID_cn> <type> '
                '<calendar> <Gregorian_day> <month> <year>')
        print '\t\t <type> value 0 for death, 1 for birthday'
        print('\t\t <calendar> value 0 for Gregorian, 1 for Chinese calendar'
                ', by which anniversaries are calculated')
        print '\t-d:\tDelete anniversary. Syntax: -d <ID_en|ID_cn>'
        sys.exit(1)
    if not 1 <= month <= 12:
        print '%s: Invalid month value: month 1-12.' % (name,)
        sys.exit(1)
    if not 1645 <= year <= 7000:
        print '%s: Invalid year value: year 1645-7000.' % (name,)
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
    ext = dict(show=opt.has_key('-s'), bencao=opt.has_key('-c'))
    if single:
        print_month(year, month, _daysinmonth[month - 1], lang, enc, ext=ext)
    else:
        lcd = None
        for i in xrange(12):
            lcd = print_month(year, i + 1, _daysinmonth[i], lang, enc, lcd, ext)
