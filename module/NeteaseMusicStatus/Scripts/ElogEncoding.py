# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-11 19:55:43
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-13 08:20:40
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogEncoding.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

from enum import Enum

class SPCEncode(Enum):
    UNKNOW = 0
    EUR = 1 # 带注音的西文
    SGN = 2 # 符号
    HAN = 3 # 汉字（已知包括：简体、繁体、日文）
    HIRA = 4 # 全角符号、平假名、片假名
    KR = 5 # 韩国谚文
    SHARP = 6 # 韩国谚文

    __all__ = None
    @classmethod
    @property
    def all(cls):
        if not cls.__all__:
            cls.__all__ = {
                cls.UNKNOW: {
                    cls.size: -2,
                    cls.codes: []
                },
                cls.EUR: {
                    cls.size: 1,
                    cls.codes: [4],
                },
                cls.SHARP: {
                    cls.size: 1,
                    cls.codes: [10],
                    cls.known:{
                        "【SHARP_10_b'\\n'】":"#"
                    }
                },
                cls.SGN: {
                    cls.size: 2,
                    cls.codes: [23, 202, 203],
                },
                cls.HAN: {
                    cls.size: 2,
                    cls.codes: [66,83,96,113,172,189],
                },
                cls.HIRA: {
                    cls.size: 2,
                    cls.codes: [6],
                },
                cls.KR: {
                    cls.size: 2,
                    cls.codes: [142,159,232,249],
                },
            }
        return cls.__all__
    
    @classmethod
    def GetByCode(cls, code:int):
        for encode in cls.all:
            if code in encode.codes:
                return encode
        return SPCEncode.UNKNOW

    @property
    def size(self):
        return SPCEncode.all[self][SPCEncode.size]

    @property
    def known(self) -> dict[str,str]:
        try:
            return SPCEncode.all[self][SPCEncode.known]
        except KeyError:
            return None

    @property
    def codes(self):
        return SPCEncode.all[self][SPCEncode.codes]

# region known Charaters
# TV动画《皿三昧》片尾曲 ；TVアニメ「さらざんまい」EDテーマ
# TV【HAN_96_153_185】【HAN_66_118_139】【HIRA_6_51_153】【HAN_66_152_207】【HAN_113_184_170】【HAN_83_186_70】【HIRA_6_51_136】【HAN_66_170_68】【HAN_96_48_222】【HAN_83_137_18】 【SGN_202_252_137】TV【HIRA_6_17_19】【HIRA_6_0_136】【HIRA_6_0_32】【HIRA_6_51_255】【HIRA_6_34_103】【HIRA_6_17_170】【HIRA_6_34_84】【HIRA6__17_1】【HIRA_6_34_222】【HIRA_6_34_119】【HIRA_6_51_238】ED【HIRA_6_0_85】【HIRA_6_0_252】【HIRA_6_0_220】

# アンコール
# 【HIRA_6_17_19】【HIRA_6_0_3】【HIRA_6_17_3】【HIRA_6_0_252】【HIRA_6_0_138】

# 最深部
# 【HAN_83_254_51】【HAN_83_71_33】【HAN_172_0_185】

# ～メインテーマ～
# 【SGN_202_237_220】【HIRA_6_0_32】【HIRA_6_17_117】【HIRA_6_0_3】【HIRA_6_0_85】【HIRA_6_0_252】【HIRA_6_0_220】【SGN_202_237_220】

#「プロポーズ大作戦」オリジナル・サウンドトラック
# 【HIRA_6_51_255】【HIRA_6_0_69】【HIRA_6_0_236】【HIRA_6_0_239】【HIRA_6_0_252】【HIRA_6_17_154】【HAN_96_117_70】【HAN_113_237_254】【HAN_83_187_87】【HIRA_6_51_238】【HIRA_6_17_155】【HIRA_6_0_155】【HIRA_6_17_184】【HIRA_6_0_153】【HIRA_6_0_138】【HIRA_6_0_139】【HIRA_6_17_101】【HIRA_6_17_87】【HIRA_6_0_3】【HIRA_6_0_170】【HIRA_6_0_187】【HIRA_6_0_168】【HIRA_6_0_0】【HIRA_6_17_206】

# 日剧《轮到你了》主题曲
# 【HAN_83_69_100】【HAN_96_170_70】【HIRA_6_51_153】【HAN_189_237_223】【HAN_96_187_48】【HAN_113_237_49】【HAN_113_154_85】【HIRA_6_51_136】【HAN_113_184_139】【HAN_172_19_186】【HAN_83_137_18】

# 张国荣
# 【HAN_96_252_49】【HAN_96_137_237】【HAN_189_238_2】

# 别话
# 【HAN_96_187_138】【HAN_189_206_239】

# 青色フィルム
# 【HAN_172_239_16】【HAN_189_170_18】【HIRA_6_0_103】【HIRA_6_17_2】【HIRA_6_0_138】【HIRA_6_0_49】

# ミルク
# 【HIRA_6_0_205】【HIRA_6_0_138】【HIRA_6_17_206】

# △
# 【SGN_23_84_3】

# たぶん
# 【HIRA_6_34_205】【HIRA_6_34_86】【HIRA_6_17_1】

# 大概
# 【HAN_96_117_70】【HAN_83_87_17】

# 动画《圣诞之吻》
# 【HAN_96_153_185】【HAN_66_118_139】【HIRA_6_51_153】【HAN_96_254_2】【HAN_189_206_220】【HAN_113_169_136】【HAN_96_50_139】【HIRA_6_51_136】

# 君のままで
# 【HAN_96_50_137】【HIRA_6_34_223】【HIRA_6_34_222】【HIRA_6_34_222】【HIRA_6_34_70】

# 做你自己
# 【HAN_96_34_152】【HAN_113_237_49】【HAN_189_68_155】【HAN_96_71_33】

# ö
# 【EUR_4_86】

# フリージア
# 【HIRA_6_0_103】【HIRA_6_0_155】【HIRA_6_0_252】【HIRA_6_17_184】 【HIRA_6_17_19】

# 张敬轩
# 【HAN_96_252_49】【HAN_83_103_253】【HAN_189_237_168】

# 我的天
# 【HAN_83_187_35】【HAN_66_152_119】【HAN_96_117_168】
# endregion known Charaters

ENCODING = {
    # 4 EUR
    
    # 6 HIRA

    # 10 SHARP (with b'\n)
    11: "3",
    12: "C",
    13: "S",
    14: "c",
    15: "s",
    
    # 23 SGN

    25: "【STX】",
    26: "2",
    27: "\"",
    28: "R",
    29: "B",
    30: "r",
    31: "b",

    40: "!",
    41: "1",

    44: "a",
    45: "q",
    46: "A",
    47: "Q",

    56: "0",
    57: " ",

    60: "p",
    61: "`",
    62: "P",
    63: "@",

    # 66 HAN
    
    72: "G",
    73: "W",
    74: "g",
    75: "w",

    78: "'",
    79: "7",

    # 83 HAN

    88: "V",
    89: "F",
    90: "v",
    91: "f",

    94: "6",
    95: "&",
    # 96 HAN

    104: "e",
    105: "u",
    106: "E",
    107: "U",
    108: "%",
    109: "5",

    # 113 HAN

    120: "t",
    121: "d",
    122: "T",
    123: "D",
    124: "4",
    125: "$",

    130: "+",
    131: ";",
    132: "K",
    133: "[",
    134: "k",
    135: "{",

    # 142 KR
    
    145: "\n",
    146: ":",
    147: "*",
    148: "Z",
    149: "J",
    150: "z",
    151: "j",

    # 159 KR

    160: ")",
    161: "9",
    162: "\t",

    164: "i",
    165: "y",
    166: "I",
    167: "Y",

    # 172 HAN

    176: "8",
    177: "(",

    180: "x",
    181: "h",
    182: "X",
    183: "H",

    # 189 HAN

    192: "O",
    193: "_",
    194: "o",

    198: "/",
    199: "?",

    # 202 SGN
    # 203 SGN

    208: "^",
    209: "N",
    210: "~",
    211: "n",

    214: ">",
    215: ".",

    224: "m",
    225: "}",
    226: "M",
    227: "]",
    228: "-",
    229: "=",

    # 232 KR
    
    240: "|",
    241: "l",
    242: "",
    243: "L",
    244: "<",
    245: ",",

    # 249 KR
}