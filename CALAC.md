#! https://zhuanlan.zhihu.com/p/358838437
# 百度实体识别工具LAC的试用感想



* *背景*

  之前在[广东省行政执法信息公示平台](http://210.76.74.232/ApprLawPublicity/index.html#/home)爬取了一些行政处罚公开数据，本想据此生成违法热力图，可惜案例信息里没有单独的字段标出案例发生地，幸运的是里面有一个字段是【违法事实】,信息如“2020年8月7日在汕头市金环南路与东方街交界西北侧步道擅自占用城市步道堆放“哈啰”共享单车、助力车，经责令整改无整改。”，包含了案例发生地，如果可以在文中中提取地点信息，问题就迎刃而解。
  
  作为一名对NLP一窍不通的小白，我需要的是一款开源的、简单易用的、无硬件要求的、准确率高的NLP框架帮我从大量语句中逐条提取地点信息，在试用几款NLP框架(jieba/HanLP/Stanza/LTP/LAC/bosonnlp)之后，最终决定使用百度的LAC（版本:2.1.1）框架。（其实bosonnlp 的准确率、易用性最好，可惜已经不对外部开发者开放使用）

---


* *踩过的坑*

  关于LAC的使用，官网上有简易教程，这里就不废话（[详情见链接](https://github.com/baidu/lac)）。这里主要讲下个人使用lac过程中发现其的坑

  * 黑箱

    一开始使用的时候，发现有些地名的识别效果不强，本想通过debug了解其工作机制，但发现其识别词性的核心方法依赖于【paddle.fluid.core_avx.PaddleBuf】,而对应类在core_avx.pyd 动态链接库中，无从下手

  * ‘一词多性’无法识别

    在“当事人薛锐河（薛锐河餐饮店）在金新路42号2幢104号房超出铺门经营饮食一案”，“薛锐河”即是作为人名，也是地名中“薛锐河餐饮店”的一部分，但LAC在输出分词及词性时，只会输出一个“薛锐河”，并且将其词性识别为LOC。

  * 歧义

    1.一些地名，如“跃进路”、“红荔市场”、“中山一横”，由于地名中的部分组成字段在其他语境下不是常见的地名名词，lac会将其识别为“跃进”-“路”、“红荔”-“市场”、“中山”-“一”-“横”；

    2.一些人名，如“当事人蓝荣城于2019年8月26日在华侨新村路1号之二前擅自占道堆放装修工具”中的“蓝荣城”，lac将其识别为LOC；

    3.部分物业小区，如“当事人于2019年5月27日在天华美地占道堆放砖块”中的“天华美地”等，lac无法将其识别为LOC；

    4.部分车牌号，如“当事人于2020年7月29日驾驶汽车车牌为豫D2FT73，在龙眼路67号擅自经营西瓜，面积2.5平方米（2.5米*1.0米）”中的“豫D2FT73”之“豫”，lac会将其识别为LOC；

    根据问题2/3/4， 猜测lac不具有词性推断能力（中文nlp的难点问题？）。
---

* *文本预处理（个人思路，欢迎探讨）*

  * 将开头不是且包含的"路"、"街"、"市场"、"苑"、"园"、"巷"、"横"、"院"、"庭" 词语认定为地点词语，部分代码如下:
  ```python
  def modifyLac(k: str):
    if (k.find('路',1)!=-1) or (k.find('街',1)!=-1) or (k.find('市场',1)!=-1) or (k.find('苑',1)!=-1) or (k.find('园',1)!=-1) or (k.find('巷',1)!=-1) or (k.find('横',1)!=-1) or (k.find('院',1)!=-1) or (k.find('庭',1)!=-1):
        return True
    else:
        return False
  ```

  * 不认为包含"店"的词语为地点信息，因为店名无法准确定位经纬度；
  * 去除文本中括号内信息，因为其信息一般作为补充修饰作用，但有时会将其误认为LOC；
  * 截取文本中，从词性为LOC到词性为['TIME', 't', 'd', 'v', 'vd', 'vn', 'PER', 'nr', 'nw','d'] 之间的字符串作为地点信息，部分代码如下:
  ```python
    lac_result = lac.run(text)
    word_list = lac_result[0]
    tag_list = lac_result[1]
    dictionary = dict(zip(word_list, tag_list))

    start_flag = False
    end_flag = False
    end_array = ['TIME', 't', 'd', 'v', 'vd', 'vn', 'PER', 'nr', 'nw','d']
    result = ''
    for k, v in dictionary.items():
        if (v == 'LOC') or (v == 'ns') or modifyLac(k):
            if not start_flag and len(k)!=1 and ('店' not in k):
                start_flag = True
        elif v in end_array:
            if start_flag:
                if (ascii_pattern.match(k)) and not modifyLac(k):
                    end_flag = True
                else:
                    end_flag = False
        if start_flag and not end_flag and not (v == 'w') :
            result += k
        if end_flag:
            break
    ```
    * 个别词语使用干预词典处理，部分代码如下:
    ```python
    # 装载干预词典, sep参数表示词典文件采用的分隔符，为None时默认使用空格或制表符'\t'
    lac.load_customization('custom.txt', sep=None)
    ```
    ---












  



    

    

    

    

    

