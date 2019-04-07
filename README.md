# Cyber Incense Burner 虚拟烧香

This project aims to provide some utilities to aid the remembrance of ancestors, in the hope of
being able to make ritual offerings like burning joss sticks in cyberspace (ultimate goal).

## pyccal.py

This script tries to mimic the console output of [ccal](https://github.com/liangqi/ccal), a perpetual calendar utility (万年历 / lịch vạn niên).
Additional functions include showing extra lines (switch `-s`) for daily sexagesimal names, miscellaneous terms (other than solar terms) for phenology,
and anniversaries of birth or death for people registered using switches like `-a`, etc. See help (`-h`) for details.

CAVEAT: The Chinese calendar is calculated using [pycalcal](https://github.com/espinielli/pycalcal), and is not as accurate as
[ccal](https://github.com/liangqi/ccal). Outputs for years beyond 2233 are not trustworthy. The performance is also inferior.

Sample output:

	>chcp
	Active code page: 936
	
	>python pyccal.py -sg 7 2018
	                   July 2018  戊戌年六月小13日始
	Sun  日   Mon  一   Tue  二   Wed  三   Thu  四   Fri  五   Sat  六
	 1 十八    2 十九    3 二十    4 廿一    5 廿二    6 廿三    7 小暑
	   甲午      乙未      丙申      丁酉      戊戌      己亥      庚子
	 8 廿五    9 廿六   10 廿七   11 廿八   12 廿九   13 六月   14 初二
	   辛丑    [外婆忌]    癸卯      甲辰     [妈生]     丙午     [出梅]
	15 初三   16 初四   17 初五   18 初六   19 初七   20 初八   21 初九
	   戊申      己酉     [初伏]     辛亥      壬子      癸丑      甲寅
	22 初十   23 大暑   24 十二   25 十三   26 十四   27 十五   28 十六
	   乙卯      丙辰      丁巳      戊午      己未     [中伏]     辛酉
	29 十七   30 十八   31 十九
	   壬戌      癸亥      甲子
	
	>python pyccal.py -s 7 2018
	                July 2018 (Year WuXu, Month 6X S13)
	Sunday    Monday    Tuesday   Wednesday Thursday  Friday    Saturday
	 1 [18]    2 [19]    3 [20]    4 [21]    5 [22]    6 [23]    7 [XS]
	  JiaWu     YiWei    BingShen  DingYou     WuXu     JiHai     GengZi
	 8 [25]    9 [26]   10 [27]   11 [28]   12 [29]   13 [ 6]Y  14 [ 2]
	 XinChou   [D.MGm]    GuiMao   JiaChen   [B.Mom]    BingWu   [ChuMei]
	15 [ 3]   16 [ 4]   17 [ 5]   18 [ 6]   19 [ 7]   20 [ 8]   21 [ 9]
	  WuShen    JiYou    [ChuFu]    XinHai    RenZi    GuiChou    JiaYin
	22 [10]   23 [DS]   24 [12]   25 [13]   26 [14]   27 [15]   28 [16]
	  YiMao    BingChen   DingSi     WuWu     JiWei   [ZhongFu]   XinYou
	29 [17]   30 [18]   31 [19]
	  RenXu     GuiHai    JiaZi
