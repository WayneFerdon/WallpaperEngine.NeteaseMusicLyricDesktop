# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:41:52
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-11-14 08:36:23
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogEncoding.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# # ----------------------------------------------------------------
# # Author: WayneFerdon wayneferdon@hotmail.com
# # Date: 2023-04-11 19:55:43
# # LastEditors: WayneFerdon wayneferdon@hotmail.com
# # LastEditTime: 2023-11-14 04:07:44
# # FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogEncoding.py
# # ----------------------------------------------------------------
# # Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# # Licensed to the .NET Foundation under one or more agreements.
# # The .NET Foundation licenses this file to you under the MIT license.
# # See the LICENSE file in the project root for more information.
# # ----------------------------------------------------------------

# from PropertyEnum import *

# class SPCEncode(PropertyEnum):
#     UNKNOW = 0
#     EUR = 1 # 带注音的西文
#     SGN = 2 # 符号
#     HAN = 3 # 汉字（已知包括：简体、繁体、日文）
#     HIRA = 4 # 全角符号、平假名、片假名
#     KR = 5 # 韩国谚文
#     SHARP = 6 # 韩国谚文

#     @enumproperty
#     def size(self) -> int: ...
#     @enumproperty
#     def known(self) -> dict[str,str]: ...
#     @enumproperty
#     def codes(self) -> list[int]: ...

#     @classmethod
#     def __init_properties__(cls) -> None:
#         cls.UNKNOW.size = -2
#         cls.EUR.size = 1
#         cls.SHARP.size = 1
#         cls.SGN.size = 2
#         cls.HAN.size = 2
#         cls.HIRA.size = 2
#         cls.KR.size = 2

#         cls.UNKNOW.codes = []
#         cls.EUR.codes = [4]
#         cls.SHARP.codes = [10]
#         cls.SGN.codes = [23, 202, 203]
#         cls.HAN.codes = [66,83,96,113,172,189]
#         cls.HIRA.codes = [6]
#         cls.KR.codes = [142,159,232,249]

#         cls.SGN.known = {
#             "【SGN_23_84_3】":"△",
#         }

#         cls.SHARP.known = {
#             "【SHARP_10_b'\\n'】":"#",
#         }

#         cls.HAN.known = {
#             "【HAN_172_19_185】":"風",
#             "【HAN_96_100_237】":"好",
#             "【HAN_189_185_51】":"言",
#             "【HAN_189_136_100】":"若",
#             "【HAN_189_0_237】":"能",
#             "【HAN_96_48_33】":"就",
#             "【HAN_189_206_116】":"说",
#             "【HAN_96_68_154】":"出",
#             "【HAN_96_84_254】":"喜",
#             "【HAN_83_253_19】":"欢",
#             "【HAN_113_237_49】":"你",
#             "【HAN_66_171_237】":"白",
#             "【HAN_189_170_18】":"色",
#             "【HAN_189_254_170】":"蜉",
#             "【HAN_189_239_2】":"蝣",
#             "【HAN_113_252_86】":"伶",
#             "【HAN_113_139_0】":"仃",
#             "【HAN_113_184_117】":"两",
#             "【HAN_113_154_154】":"人",
#             "【HAN_172_138_186】":"高",
#             "【HAN_66_51_253】":"瀬",
#             "【HAN_66_101_33】":"統",
#             "【HAN_113_169_205】":"也",
#             "【HAN_172_68_221】":"野",
#             "【HAN_66_118_48】":"田",
#             "【HAN_83_119_137】":"愛",
#             "【HAN_96_223_205】":"実",
#             "【HAN_113_184_154】":"为",
#             "【HAN_113_139_51】":"什",
#             "【HAN_113_169_187】":"么",
#             "【HAN_96_237_139】":"彻",
#             "【HAN_96_117_254】":"夜",
#             "【HAN_96_169_207】":"广",
#             "【HAN_83_16_236】":"播",
#         }
#         cls.HIRA.known = {
#             "【HIRA_6_17_153】":"り",
#             "【HIRA_6_17_170】":"ら",
#             "【HIRA_6_17_187】":"よ",
#             "【HIRA_6_34_168】":"ど",
#             "【HIRA_6_34_85】":"う",
#             "【HIRA_6_34_69】":"し",
#             "【HIRA_6_34_87】":"て",
#             "【HIRA_6_34_17】":"あ",
#             "【HIRA_6_34_49】":"だ",
#             "【HIRA_6_34_185】":"と",
#             "【HIRA_6_34_187】":"え",
#             "【HIRA_6_34_205】":"た",
#             "【HIRA_6_34_223】":"の",
#             "【HIRA_6_34_238】":"き",
#             "【HIRA_6_34_101】":"ふ",
#             "【HIRA_6_34_252】":"ぼ",
#             "【HIRA_6_34_2】":"っ",
#             "【HIRA_6_34_32】":"ち",
#             "【HIRA_6_17_184】":"ジ",
#             "【HIRA_6_0_2 】":"ャ",
#             "【HIRA_6_17_169】":"ス",
#             "【HIRA_6_0_85】":"テ",
#             "【HIRA_6_17_2】":"ィ",
#             "【HIRA_6_17_169】":"ス",
#             "【HIRA_6_17_117】":"イ",
#             "【HIRA_6_0_3】":"ン",
#             "【HIRA_6_17_86】":"ザ",
#             "【HIRA_6_0_254】":"ボ",
#             "【HIRA_6_0_0】":"ッ",
#             "【HIRA_6_17_206】":"ク",
#             "【HIRA_6_17_169】":"ス",
#             "【HIRA_6_17_207】":"タ",
#             "【HIRA_6_0_170】":"ド",
#             "【HIRA_6_0_50】":"バ",
#             "【HIRA_6_0_205】":"ミ",
#             "【HIRA_6_0_252】":"ー",
#             "【HIRA_6_17_155】":"オ",
#             "【HIRA_6_0_138】":"ル",
#             "【HIRA_6_0_153】":"ナ",
#             "【HIRA_6_0_187】":"ト",
#             "【HIRA_6_0_253】":"レ",
#             "【HIRA_6_0_68】":"デ",
#             "【HIRA_6_17_155】":"オ",
#         }
        
#     @classmethod
#     def GetByCode(cls, code:int):
#         for encode in cls.definitions:
#             if code in encode.codes:
#                 return encode
#         return SPCEncode.UNKNOW

# # region known Charaters
# # TV动画《皿三昧》片尾曲 ；TVアニメ「さらざんまい」EDテーマ
# # TV【HAN_96_153_185】【HAN_66_118_139】【HIRA_6_51_153】【HAN_66_152_207】【HAN_113_184_170】【HAN_83_186_70】【HIRA_6_51_136】【HAN_66_170_68】【HAN_96_48_222】【HAN_83_137_18】 【SGN_202_252_137】TV【HIRA_6_17_19】【HIRA_6_0_136】【HIRA_6_0_32】【HIRA_6_51_255】【HIRA_6_34_103】【HIRA_6_17_170】【HIRA_6_34_84】【HIRA6__17_1】【HIRA_6_34_222】【HIRA_6_34_119】【HIRA_6_51_238】ED【HIRA_6_0_85】【HIRA_6_0_252】【HIRA_6_0_220】

# # アンコール
# # 【HIRA_6_17_19】【HIRA_6_0_3】【HIRA_6_17_3】【HIRA_6_0_252】【HIRA_6_0_138】

# # 最深部
# # 【HAN_83_254_51】【HAN_83_71_33】【HAN_172_0_185】

# # ～メインテーマ～
# # 【SGN_202_237_220】【HIRA_6_0_32】【HIRA_6_17_117】【HIRA_6_0_3】【HIRA_6_0_85】【HIRA_6_0_252】【HIRA_6_0_220】【SGN_202_237_220】

# #「プロポーズ大作戦」オリジナル・サウンドトラック
# # 【HIRA_6_51_255】【HIRA_6_0_69】【HIRA_6_0_236】【HIRA_6_0_239】【HIRA_6_0_252】【HIRA_6_17_154】【HAN_96_117_70】【HAN_113_237_254】【HAN_83_187_87】【HIRA_6_51_238】【HIRA_6_17_155】【HIRA_6_0_155】【HIRA_6_17_184】【HIRA_6_0_153】【HIRA_6_0_138】【HIRA_6_0_139】【HIRA_6_17_101】【HIRA_6_17_87】【HIRA_6_0_3】【HIRA_6_0_170】【HIRA_6_0_187】【HIRA_6_0_168】【HIRA_6_0_0】【HIRA_6_17_206】

# # 日剧《轮到你了》主题曲
# # 【HAN_83_69_100】【HAN_96_170_70】【HIRA_6_51_153】【HAN_189_237_223】【HAN_96_187_48】【HAN_113_237_49】【HAN_113_154_85】【HIRA_6_51_136】【HAN_113_184_139】【HAN_172_19_186】【HAN_83_137_18】

# # 张国荣
# # 【HAN_96_252_49】【HAN_96_137_237】【HAN_189_238_2】

# # 别话
# # 【HAN_96_187_138】【HAN_189_206_239】

# # 青色フィルム
# # 【HAN_172_239_16】【HAN_189_170_18】【HIRA_6_0_103】【HIRA_6_17_2】【HIRA_6_0_138】【HIRA_6_0_49】

# # ミルク
# # 【HIRA_6_0_205】【HIRA_6_0_138】【HIRA_6_17_206】

# # △
# # 【SGN_23_84_3】

# # たぶん
# # 【HIRA_6_34_205】【HIRA_6_34_86】【HIRA_6_17_1】

# # 大概
# # 【HAN_96_117_70】【HAN_83_87_17】

# # 动画《圣诞之吻》
# # 【HAN_96_153_185】【HAN_66_118_139】【HIRA_6_51_153】【HAN_96_254_2】【HAN_189_206_220】【HAN_113_169_136】【HAN_96_50_139】【HIRA_6_51_136】

# # 君のままで
# # 【HAN_96_50_137】【HIRA_6_34_223】【HIRA_6_34_222】【HIRA_6_34_222】【HIRA_6_34_70】

# # 做你自己
# # 【HAN_96_34_152】【HAN_113_237_49】【HAN_189_68_155】【HAN_96_71_33】

# # ö
# # 【EUR_4_86】

# # フリージア
# # 【HIRA_6_0_103】【HIRA_6_0_155】【HIRA_6_0_252】【HIRA_6_17_184】 【HIRA_6_17_19】

# # 张敬轩
# # 【HAN_96_252_49】【HAN_83_103_253】【HAN_189_237_168】

# # 我的天
# # 【HAN_83_187_35】【HAN_66_152_119】【HAN_96_117_168】
# # endregion known Charaters

# ENCODING = {
#     # 4 EUR
    
#     # 6 HIRA

#     # 10 SHARP (with b'\n')
#     11: "3",
#     12: "C",
#     13: "S",
#     14: "c",
#     15: "s",
    
#     # 23 SGN

#     25: "【STX】",
#     26: "2",
#     27: "\"",
#     28: "R",
#     29: "B",
#     30: "r",
#     31: "b",

#     40: "!",
#     41: "1",

#     44: "a",
#     45: "q",
#     46: "A",
#     47: "Q",

#     56: "0",
#     57: " ",

#     60: "p",
#     61: "`",
#     62: "P",
#     63: "@",

#     # 66 HAN
    
#     72: "G",
#     73: "W",
#     74: "g",
#     75: "w",

#     78: "'",
#     79: "7",

#     # 83 HAN

#     88: "V",
#     89: "F",
#     90: "v",
#     91: "f",

#     94: "6",
#     95: "&",
#     # 96 HAN

#     104: "e",
#     105: "u",
#     106: "E",
#     107: "U",
#     108: "%",
#     109: "5",

#     # 113 HAN

#     120: "t",
#     121: "d",
#     122: "T",
#     123: "D",
#     124: "4",
#     125: "$",

#     130: "+",
#     131: ";",
#     132: "K",
#     133: "[",
#     134: "k",
#     135: "{",

#     # 142 KR
    
#     145: "\n",
#     146: ":",
#     147: "*",
#     148: "Z",
#     149: "J",
#     150: "z",
#     151: "j",

#     # 159 KR

#     160: ")",
#     161: "9",
#     162: "\t",

#     164: "i",
#     165: "y",
#     166: "I",
#     167: "Y",

#     # 172 HAN

#     176: "8",
#     177: "(",

#     180: "x",
#     181: "h",
#     182: "X",
#     183: "H",

#     # 189 HAN

#     192: "O",
#     193: "_",
#     194: "o",

#     198: "/",
#     199: "?",

#     # 202 SGN
#     # 203 SGN

#     208: "^",
#     209: "N",
#     210: "~",
#     211: "n",

#     214: ">",
#     215: ".",

#     224: "m",
#     225: "}",
#     226: "M",
#     227: "]",
#     228: "-",
#     229: "=",

#     # 232 KR
    
#     240: "|",
#     241: "l",
#     243: "L",
#     244: "<",
#     245: ",",
#     242: "",

#     # 249 KR
# }