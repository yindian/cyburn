#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import os.path
import getopt
import sqlite3
import struct
import traceback
import zlib
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
_en_miscterm = [
        'RuMei', 'ChuMei', 'ChuFu', 'ZhongFu', 'MoFu',
        'YiJiu', 'ErJiu', 'SanJiu', 'SiJiu', 'WuJiu',
        'LiuJiu', 'QiJiu', 'BaJiu', 'JiuJiu']
_chs_miscterm = [
        u'入梅', u'出梅', u'初伏', u'中伏', u'末伏',
        u'一九', u'二九', u'三九', u'四九', u'五九',
        u'六九', u'七九', u'八九', u'九九']
_miscterm_fmt = '[%s]'
_anniv_fmt = '[%s]'
_en_anniv_birth_fmt = 'B.%(ID)s%(mul)s'
_en_anniv_death_fmt = 'D.%(ID)s%(mul)s'
_chs_anniv_birth_fmt = u'%(ID)s生%(mul)s'
_chs_anniv_death_fmt = u'%(ID)s忌%(mul)s'

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
        miscterm = _en_miscterm
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
        anniv_birth_fmt = _en_anniv_birth_fmt
        anniv_death_fmt = _en_anniv_death_fmt
    else:
        solterms = _chs_solterms
        daynames = _chs_daynames
        stems    = _chs_stems
        branches = _chs_branches
        miscchar = _chs_miscchar
        miscterm = _chs_miscterm
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
        anniv_birth_fmt = _chs_anniv_birth_fmt
        anniv_death_fmt = _chs_anniv_death_fmt
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
    cmonth = c_date.month
    sameday = False
    show = ext.get('show')
    if show:
        stem, branch = pcc.chinese_day_name(date)
        stem -= 1
        branch -= 1
        anniv = ext.get('anniv')
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
                cmonth = c_new_moon_date.month
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
                    cmonth = c_new_moon_date.month
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
                cr = get_anniv_on(anniv, year, month, dcnt, cmonth, ldcnt)
                if cr:
                    if cr[0]:
                        if len(cr[0]) > 1:
                            cr[0] = anniv_birth_fmt % {
                            'ID': '', 'mul': 'x%d' % (len(cr[0]),)}
                        else:
                            cr[0] = anniv_birth_fmt % {
                            'ID': cr[0][0][int(lang != 'en')], 'mul': ''}
                    else:
                        cr[0] = ''
                    if cr[1]:
                        if len(cr[1]) > 1:
                            cr[1] = anniv_death_fmt % {
                            'ID': '', 'mul': 'x%d' % (len(cr[1]),)}
                        else:
                            cr[1] = anniv_death_fmt % {
                            'ID': cr[1][0][int(lang != 'en')], 'mul': ''}
                    else:
                        cr[1] = ''
                    s = _anniv_fmt % (''.join(cr),)
                elif month == 6: # check RuMei
                    if not ext.has_key('RuMei') or ext['RuMei'][0] != year:
                        t, b = pcc.chinese_day_name(minor_solterm_date)
                        if not ext.get('bencao'):
                            if t <= 3:
                                ext['RuMei'] = (year, minor_solterm_date + 3-t)
                            else:
                                ext['RuMei'] = (year, minor_solterm_date +13-t)
                        else:
                            if t <= 9:
                                ext['RuMei'] = (year, minor_solterm_date + 9-t)
                            else:
                                ext['RuMei'] = (year, minor_solterm_date +19-t)
                    if date == ext['RuMei'][1]:
                        s = _miscterm_fmt % (miscterm[0],)
                    if not ext.has_key('XZ') or ext['XZ'][0] != year:
                        t, b = pcc.chinese_day_name(major_solterm_date)
                        ext['XZ'] = (year, major_solterm_date, t, b)
                elif month == 7: # check ChuMei, ChuFu, ZhongFu
                    if not ext.has_key('ChuMei') or ext['ChuMei'][0] != year:
                        t, b = pcc.chinese_day_name(minor_solterm_date)
                        if not ext.get('bencao'):
                            if b <= 8:
                                ext['ChuMei'] = (year, minor_solterm_date +8-b)
                            else:
                                ext['ChuMei'] = (year, minor_solterm_date +20-b)
                        else:
                            if t <= 9:
                                ext['ChuMei'] = (year, minor_solterm_date +9-t)
                            else:
                                ext['ChuMei'] = (year, minor_solterm_date +19-t)
                    if not ext.has_key('XZ') or ext['XZ'][0] != year:
                        d = pcc.fixed_from_moment(
                                pcc.major_solar_term_on_or_after(date - 30))
                        t, b = pcc.chinese_day_name(d)
                        ext['XZ'] = (year, d, t, b)
                    if not ext.has_key('ChuFu') or ext['ChuFu'][0] != year:
                        _, d, t, b = ext['XZ']
                        if t <= 7:
                            ext['ChuFu'] = (year, d + 27 - t, d + 37 - t)
                        else:
                            ext['ChuFu'] = (year, d + 37 - t, d + 47 - t)
                    if date == ext['ChuMei'][1]:
                        s = _miscterm_fmt % (miscterm[1],)
                    elif date == ext['ChuFu'][1]:
                        s = _miscterm_fmt % (miscterm[2],)
                    elif date == ext['ChuFu'][2]:
                        s = _miscterm_fmt % (miscterm[3],)
                elif month == 8: # check ZhongFu, MoFu
                    if not ext.has_key('XZ') or ext['XZ'][0] != year:
                        d = pcc.fixed_from_moment(
                                pcc.major_solar_term_on_or_after(date - 61))
                        t, b = pcc.chinese_day_name(d)
                        ext['XZ'] = (year, d, t, b)
                    if not ext.has_key('ChuFu') or ext['ChuFu'][0] != year:
                        _, d, t, b = ext['XZ']
                        if t <= 7:
                            ext['ChuFu'] = (year, d + 27 - t, d + 37 - t)
                        else:
                            ext['ChuFu'] = (year, d + 37 - t, d + 47 - t)
                    if not ext.has_key('MoFu') or ext['MoFu'][0] != year:
                        t, b = pcc.chinese_day_name(minor_solterm_date)
                        if t <= 7:
                            ext['MoFu'] = (year, minor_solterm_date + 7 - t)
                        else:
                            ext['MoFu'] = (year, minor_solterm_date + 17 - t)
                    if date == ext['ChuFu'][2]:
                        s = _miscterm_fmt % (miscterm[3],)
                    elif date == ext['MoFu'][1]:
                        s = _miscterm_fmt % (miscterm[4],)
                elif month == 12 or month < 4: # check *Jiu
                    if not ext.has_key('DZ') or ext['DZ'][0] != year - int(
                            month != 12):
                        if month == 12:
                            d = major_solterm_date
                            ext['DZ'] = (year, d)
                        else:
                            d = pcc.fixed_from_moment(
                                    pcc.major_solar_term_on_or_after(
                                        pcc.fixed_from_gregorian(
                                            (year - 1, 12, 1))))
                            ext['DZ'] = (year - 1, d)
                        ext['Jiu'] = set([d + 9 * i for i in xrange(9)])
                    if date in ext['Jiu']:
                        d = date - ext['DZ'][1]
                        s = _miscterm_fmt % (miscterm[5 + d / 9],)
                x = len(filter(lambda c: ord(c) > 0xFF, s))
                if len(s) + x <= 10:
                    s = s.center(10 - x)
                else:
                    x = 8 - int(ord(s[-1]) > 0xFF)
                    cr = []
                    for j in xrange(len(s) - 1):
                        x -= 1 + int(ord(s[j]) > 0xFF)
                        if x > 0:
                            cr.append(s[j])
                        elif x == 0:
                            break
                        else:
                            cr.append('.')
                            break
                    cr.append('..')
                    cr.append(s[-1])
                    s = ''.join(cr)
                    x = len(filter(lambda c: ord(c) > 0xFF, s))
                    assert len(s) + x == 10
                br.append(s)
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

def init_tables(db):
    db.execute('create table Anniv ('
            'ID_en  text not null, '
            'ID_cn  text not null, '
            'birth  boolean, '
            'ccal   boolean, '
            'gdate  date not null, '
            'cmonth integer, ' # regardless of leap
            'cday   integer, '
            'crc    integer'
            ', unique (ID_en, birth)'
            ', unique (ID_cn, birth)'
            ')')
    db.commit()

def crc_dates(gdate, cmonth, cday):
    s = struct.pack('!H4B', gdate.year, gdate.month, gdate.day, cmonth, cday)
    return zlib.crc32(s) & 0xffffffff

_crc_indicator = {
        True:   '  ',
        False:  '! ',
        }
def print_anniv_list(db, f=sys.stdout):
    enc = sys.getfilesystemencoding() or 'utf-8'
    def println(s):
        print >> f, s.encode(enc)
    cur = db.execute('select * from Anniv')
    println(_crc_indicator[True] + '\t'.join(
        [x[0] != 'gdate' and x[0] or x[0] + '     ' for x in cur.description]))
    for row in cur:
        crc = crc_dates(row['gdate'], row['cmonth'] or 0, row['cday'] or 0)
        println(_crc_indicator[crc == row['crc']] + '\t'.join(map(unicode,row)))

def parse_anniv(db):
    d = [{}, {}] # g, c
    for row in db.execute('select * from Anniv'):
        crc = crc_dates(row['gdate'], row['cmonth'] or 0, row['cday'] or 0)
        if crc == row['crc']:
            gdate = row['gdate']
            if row['ccal']:
                d[1].setdefault((row['cmonth'], row['cday']), []).append(
                        (row['ID_en'], row['ID_cn'], row['birth'], gdate))
            else:
                d[0].setdefault((gdate.month, gdate.day), []).append(
                        (row['ID_en'], row['ID_cn'], row['birth'], gdate))
        else:
            print >> sys.stderr, 'CRC failure:', '\t'.join(map(unicode, row))
    return d

def get_anniv_on(anniv, year, month, day, cmonth, cday):
    if not anniv:
        return
    gdate = dt.date(year, month, day)
    ar = []
    br = []
    d = {
            True:   ar,
            False:  br,
            }
    for row in anniv[0].get((month, day), []):
        if gdate >= row[-1]:
            d[row[2]].append(row)
    for row in anniv[1].get((cmonth, cday), []):
        if gdate >= row[-1]:
            d[row[2]].append(row)
    if ar or br:
        return [ar, br]

def add_anniv(db, ID_en, ID_cn, birth, ccal, gdate):
    date = pcc.fixed_from_gregorian((gdate.year, gdate.month, gdate.day))
    c_date = CDate_from_fixed(date)
    crc = crc_dates(gdate, c_date.month, c_date.day)
    db.execute('insert into Anniv values ('
            '?, ?, ?, ?, '
            '?, ?, ?, ?)',
            (ID_en, ID_cn, birth, ccal,
            gdate, c_date.month, c_date.day, crc))
    db.commit()

def del_anniv(db, ID):
    db.execute('delete from Anniv where ID_en = ? or ID_cn = ?', (ID, ID))
    db.commit()

def get_db():
    fname = os.path.join(os.environ.get('HOME') or os.environ['USERPROFILE'],
            '.%s.db'%(os.path.splitext(os.path.basename(sys.argv[0]))[0],))
    db = sqlite3.connect(fname,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db.row_factory = sqlite3.Row
    if os.stat(fname).st_size == 0:
        init_tables(db)
    return db

if __name__ == '__main__':
    name = os.path.basename(sys.argv[0])
    year, month = dt.date.today().timetuple()[:2]
    single = True
    try:
        opt, args = getopt.getopt(sys.argv[1:], 'gusla:d:c')
        opt = dict(opt)
        assert sum(map(int, map(opt.has_key, ('-l', '-a', '-d')))) <= 1
        if opt.has_key('-l') or opt.has_key('-d'):
            assert len(args) == 0
            if opt.has_key('-d'):
                assert opt['-d']
                try:
                    opt['-d'].decode('ascii')
                except:
                    opt['-d'] = opt['-d'].decode(sys.getfilesystemencoding()
                            or 'utf-8')
        elif opt.has_key('-a'):
            assert len(args) == 6
            try:
                ar = [opt['-a']]
                assert ar[0]
                ar[0].decode('ascii')
                assert args[0]
                ar.append(args[0].decode(sys.getfilesystemencoding()
                    or 'utf-8'))
                ar.append(bool(int(args[1])))
                ar.append(bool(int(args[2])))
                day, month, year = map(int, args[3:])
                ar.append(dt.date(year, month, day))
                opt['-a'] = ar
            except:
                traceback.print_exc()
                raise
        elif len(args) == 1:
            year = int(args[0])
            single = False
        elif len(args) == 2:
            month, year = map(int, args)
        elif args:
            print '%s: Too many parameters.' % (name,)
            raise
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
    if opt.has_key('-s'):
        _en_branches[3] = 'Mao'
    ext = dict(show=opt.has_key('-s'), bencao=opt.has_key('-c'))
    if opt.has_key('-l'):
        print_anniv_list(get_db())
        sys.exit(0)
    elif opt.has_key('-a'):
        add_anniv(get_db(), *opt['-a'])
        sys.exit(0)
    elif opt.has_key('-d'):
        del_anniv(get_db(), opt['-d'])
        sys.exit(0)
    elif opt.has_key('-s'):
        ext['anniv'] = parse_anniv(get_db())
    if single:
        print_month(year, month, _daysinmonth[month - 1], lang, enc, ext=ext)
    else:
        lcd = None
        for i in xrange(12):
            lcd = print_month(year, i + 1, _daysinmonth[i], lang, enc, lcd, ext)
