import requests
import json
import pymongo
import datetime
import time


def changeApData(apData):
    dcdCode = apData['dcdCode']
    return dcdCode


def addPunishItem(cmp: pymongo.collection.Collection, apDataList: list):
    resultList = []
    for apData in apDataList:
        dcdCode = apData['dcdCode']

        try:
            requests.adapters.DEFAULT_RETRIES = 5
            # 获取具体信息
            r3 = requests.get(
                'http://210.76.74.232/appr-law-datacenter-service/law/datacenter/publicity/2/'
                + dcdCode,
                timeout=(5, 5))
        except Exception as e:
            resultList.append(apData)
            print("Request failed :" + dcdCode)
            continue

        deatil = json.loads(r3.text)['data']
        item = {
            'dcdCode': deatil['dcdCode'],
            # 1:法人及其他组织|2:自然人|3:个体工商户
            'admCounterCategory': deatil['admCounterCategory'],
            'admCounterName': deatil['admCounterName'],
            'caseName': deatil['caseName'],
            'decisionNum': deatil['decisionNum'],
            'illegalBasis': deatil['illegalBasis'],
            'illegalFact': deatil['illegalFact'],
            'punishBasis': deatil['punishBasis'],
            'punishDate': deatil['punishDate'],
            'punishDate': deatil['punishDate'],
            'punishType': deatil['punishTypeModels'][0]['punishType'],  # 2:罚款
            'punishAmount':
            deatil['punishTypeModels'][0]['punishAmount'],  # 单位:万
            'remark': deatil['remark']
        }
        print('Loaded successfully: ' + dcdCode)
        cmp.insert_one(item)
        time.sleep(0.1)
    return resultList


def main():
    starttime = datetime.datetime.now()

    flag = '0'
    legalDepId = 'af73c8b06104479da341220946bda951'  # 汕头市金平区城市管理和综合执法局
    itemType = '2'  # 2:行政处罚 4:行政许可

    # 获取总数
    r1 = requests.get(
        'http://210.76.74.232/appr-law-datacenter-service/law/datacenter/result/list',
        params={
            'flag': flag,
            'legalDepId': legalDepId,
            'itemType': itemType,
            'pageIndex': '1',
            'pageRowNum': '1'
        })

    totalRow = json.loads(r1.text)['data']['pageObj']['totalRow']

    print("Total number of pages is " + str(totalRow))

    # 获取编号列表
    print("Loading List")
    r2 = requests.get(
        'http://210.76.74.232/appr-law-datacenter-service/law/datacenter/result/list',
        params={
            'flag': flag,
            'legalDepId': legalDepId,
            'itemType': itemType,
            'pageIndex': '1',
            'pageRowNum': totalRow
        })

    apDataList = json.loads(r2.text)['data']['dataList']

    print("Loading MongoDB")
    mgclient = pymongo.MongoClient('mongodb://localhost:37017/')
    mgdb = mgclient['JPCM']
    cmp = mgdb['cmp']

    # 全量更新,先删掉之前的数据
    cmp.delete_many({})

    #全量更新
    print("Loading Data")
    tryList = addPunishItem(cmp, apDataList)
    tryList = addPunishItem(cmp, tryList)

    #失败后再重试
    failList = addPunishItem(cmp, tryList)
    print('Failur list as follow:')
    print(list(map(changeApData, failList)))

    endtime = datetime.datetime.now()
    print("Data loaded successfully!It cost " +
          str((endtime - starttime).seconds) + " seconds")


if __name__ == '__main__':
    main()
