#coding: utf-8

#util
from data import *
from read_conf import config
from optparse import OptionParser
import csv
import cPickle as pickle
from operator import itemgetter

dp = config("../conf/dp.conf")

#rake
from rake import Rake
rake = Rake()

#nltk
import nltk

#math
import math
from math import log

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

#类似于关联规则的启发式规则
def asrule():
    print "得到非duplicate的结果"

    print "读入结果"
    f = open(dp["word_tag"],"rb")
    word_tag = pickle.load(f)
    print len(word_tag)

    f = open(dp["tag"],"rb")
    tag = pickle.load(f)
    print len(tag)

    f = open(dp["word_count"],"rb")
    word_count = pickle.load(f)
    print len(word_count)
    
    a = 0
    f = open(dp["ntag_test"])
    #f = open(dp["ntag_train"])
    ndup_test = {}
    reader = csv.reader(f)
    for line in reader:
        result = {}
        text = line[1]
        if len(line[1]) == 0:
            text = line[2]
            
        if len(text) != 0:
            keyword = rake.run(text)
            for (word,score) in keyword:
                if word in word_tag:
                    #all_tag 表示有多少标签跟这个词共现的
                    all_tag = word_tag[word]
                    if len(all_tag) < 10000:
                        for one_tag in all_tag:
                            if one_tag in result:
                                result[one_tag] += all_tag[one_tag] /word_count[word]
                            else:
                                result[one_tag] = all_tag[one_tag] /word_count[word]

            #for one_tag in result:
            #    result[one_tag] -= tag[one_tag]/20.0
            result = sorted(result.iteritems(),key=itemgetter(1),reverse=True)
        
        
        if len(result) >5:
            result = result[:5]
            #print line[1]
            #print result
            #print "result",line[-1]
            #print 30*"="
        if len(result) == 0:
            rs = "java python php"
        else:
            rs = ""
            for (w,t) in result:
                rs += (w+" ")
        ndup_test[line[0]] = rs
        a += 1
        if a % 100 == 0:
            print a
    return ndup_test
    
def main(options):
    if options.stra == "benchmark":
        ndup_test = benchmark()
    elif options.stra == "asrule":
        ndup_test = asrule()

    gen_submission(ndup_test,comp=True)

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-s","--strategy",dest="stra",action="store",\
                      help=u"选择你要使用什么策略",type="string")
    (options, args) = parser.parse_args()
    #执行判断
    print options
    main(options)
