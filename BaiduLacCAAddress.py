from LAC import LAC
import re
import numpy as np
import pandas as pd
import pymongo

china_mode = '[\u4e00-\u9fa5]'
ascii_pattern = re.compile(china_mode, re.ASCII)

lac = LAC(mode='lac')
lac.load_customization('/home/yangzake/OI/ca.txt', sep=None)


def modifyLac(k: str):
    if (k.find('路', 1) != -1) or (k.find('街', 1) != -1) or (k.find(
            '市场', 1) != -1) or (k.find('苑', 1) != -1) or (k.find(
                '园', 1) != -1) or (k.find('巷', 1) != -1) or (k.find(
                    '横', 1) != -1) or (k.find('院', 1) != -1) or (k.find(
                        '庭', 1) != -1):
        return True
    else:
        return False


def getCaseAddress(text: str):
    # 去除括号内容
    text = re.sub(u"\\（.*?）|\\{.*?}|\\[.*?]|\\【.*?】", "", text)

    text = text.replace('汕头市', '').replace('汕头',
                                           '').replace('金平区',
                                                       '').replace('金平', '')

    lac_result = lac.run(text)

    word_list = lac_result[0]
    tag_list = lac_result[1]

    dictionary = dict(zip(word_list, tag_list))

    start_flag = False
    end_flag = False
    end_array = ['TIME', 't', 'd', 'v', 'vd', 'vn', 'PER', 'nr', 'nw', 'd']
    result = ''
    for k, v in dictionary.items():
        if (v == 'LOC') or (v == 'ns') or modifyLac(k):
            if not start_flag and len(k) != 1 and ('店' not in k):
                start_flag = True
        elif v in end_array:
            if start_flag:
                if (ascii_pattern.match(k)) and not modifyLac(k):
                    end_flag = True
                else:
                    end_flag = False
        # elif (k == '，') or (k == ','):
        #     if start_flag:
        #         end_flag = True
        # elif (k == '"') or (k == '“'):
        #     if start_flag:
        #         end_flag = True
        if start_flag and not end_flag and not (v == 'w'):
            result += k
        if end_flag:
            break
    #result = '汕头市金平区' + result
    print(dictionary)
    # print(result)
    return result


def main():

    # client = pymongo.MongoClient('127.0.0.1', 37017)
    # collection = client["JPCM"]["cmp"]
    # dd = collection.find({}, {
    #     'dcdCode': 0,
    #     '_id': 0,
    #     'punishType': 0
    # })  # 去除无意义字段
    # dd = list(dd)
    #
    # data = pd.DataFrame(dd)
    # data['pre_address'] = data['illegalFact'].apply(getCaseAddress)
    # data.to_excel('/home/yangzake/OI/ca.xlsx', index=False)
    # print('done')

    text = '当事人于2019年11月27日在潮汕路西侧将餐厨垃圾排入下水道'
    result = getCaseAddress(text)
    print(result)


main()