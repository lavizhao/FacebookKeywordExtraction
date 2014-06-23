#coding: utf-8

#util
from data import *
from read_conf import config
from optparse import OptionParser
import csv
import cPickle as pickle
from operator import itemgetter
from nlp import nlp

mnlp = nlp()

dp = config("../conf/dp.conf")

#rake
from rake import Rake
rake = Rake()

#nltk
import nltk

#math
import math
from math import log

print "读入数据文件"
f = open(dp["word_tag"],"rb")
word_tag = pickle.load(f)
print len(word_tag)

f = open(dp["tag"],"rb")
tag = pickle.load(f)
print len(tag)

f = open(dp["word_count"],"rb")
word_count = pickle.load(f)
print len(word_count)

f = open(dp["tagrel"],"rb")
tagrel = pickle.load(f)
print len(tagrel)

tag_set = {}
for key in tag:
    tag_set[key.lower()] = key

def benchmark():
    print "得到非duplicate的结果"
    a = 0
    f = open(dp["other_test"])
    ndup_test = {}
    reader = csv.reader(f)
    for line in reader:
        ndup_test[line[0]] = "java python php"
        a += 1
        if a % 100000 == 0:
            print a
    return ndup_test

#这个函数是利用text 推荐tag，text可以选择为body或者title    
def context_recommender(text):
    result = {}
    keyword = rake.run(text)
    #对于title中的每一个抽取出来的词
    for (word,score) in keyword:
        #如果这个词，word_tag有记录，则获得这个记录的所有tag
        if word in word_tag:
            all_tag = word_tag[word]
            #在这里为了，节省时间，进行判断，如果小于3000个tag才用这个词
            if len(all_tag) < 3000:
                #对于这些tag的每个tag来说
                for one_tag in all_tag:
                    if one_tag in result:
                        result[one_tag] += all_tag[one_tag]/word_count[word]
                    else:
                        result[one_tag] = all_tag[one_tag]/word_count[word]
    return result
    
#这个函数主要利用    
def title_tag_recommender(title,body):
    result = {}
    #过程是这样的，先处理title，如果title不能推荐五个以上的tag，则利用body，继续进行推荐
    if len(title) != 0:
        title_result = context_recommender(title)
        #如果title推荐的个数小于5个的话
        if len(title_result) < 5:
            if len(body) >0:
                body_result = context_recommender(body)
                for one_tag in body_result:
                    #如果one_tag的结果不在title推荐的result中，那么将其除以10，在继续推荐过去，为什么这样做呢，因为title推荐的质量高一些
                    if one_tag not in title_result:
                        title_result[one_tag] = body_result[one_tag]*1.0/10
                return title_result
            else:
                return title_result
        else:
            return title_result    
    #一般来说，title如果是空，那么一般body也是空，但是为了以防万一，还是做一下
    else:
        if len(body) == 0:
            return result
        else :
            return context_recommender(body)
            
#类似于字符串匹配一样的推荐
def basic_recommender(title,body):
    result = {}
    
    #先tokenize title和body
    title_tokens,body_tokens = mnlp.title_tokenize(title),mnlp.title_tokenize(body)

    #如果两个都为0
    if len(title_tokens) == 0 and len(body_tokens) == 0:
        return [("java",0),("python",0),("php",0)]
    else:
        #先对于title的每个词来说
        for word in title_tokens:
            if word in tag_set:
                #这个词的值是word的出现次数
                result[tag_set[word]] = tag[tag_set[word]]
        #对于每个body来说
        for word in body_tokens:
            if word in tag_set and word not in result:
                result[tag_set[word]] = tag[tag_set[word]] * 0.6

        #给他们排一下顺序
        result = sorted(result.iteritems(),key=itemgetter(1),reverse=True)
        if len(result) > 5 :
            return result[:5]
        else:
            return result
            
#类似于关联规则的启发式规则
def recommend():
    print "得到非duplicate的结果"
    a = 0
    f = open(dp["ntag_test"])
    #f = open(dp["ntag_train"])
    ndup_test = {}
    reader = csv.reader(f)
    for line in reader:
        result = title_tag_recommender(line[1],line[2])
        result = sorted(result.iteritems(),key=itemgetter(1),reverse=True)
        
        if len(result) >= 5:
            result = result[:5]
            #print line[1]
            #print result
            #print "result",line[-1]
            #print 30*"="
                
        if len(result) == 0:
            result = basic_recommender(line[1],line[2])
            result = [i for (i,j) in result ]
            rs = ' '.join(result)
        else:
            rs = ""
            result = [i for (i,j) in result ]
            rs = ' '.join(result)
        ndup_test[line[0]] = rs
        a += 1
        if a % 100 == 0:
            print a
    return ndup_test
    
def main(options):
    if options.stra == "benchmark":
        ndup_test = benchmark()
    elif options.stra == "recommender":
        ndup_test = recommend()

    gen_submission(ndup_test,comp=True)

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-s","--strategy",dest="stra",action="store",\
                      help=u"选择你要使用什么策略",type="string")
    (options, args) = parser.parse_args()
    #执行判断
    print options
    main(options)
