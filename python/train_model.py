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

    a = 0
    f = open(dp["other_test"])
    ndup_test = {}
    reader = csv.reader(f)
    for line in reader:
        keyword = rake.run(line[1])
        result = {}
        for (w,s) in keyword:
            if w in word_tag:
                atag = word_tag[w]
                for aatag in atag:
                    if aatag in result:
                        result[aatag] += atag[aatag] 
                    else:
                        result[aatag] = atag[aatag] 
        
        #for atag in result:
        #    result[atag] += log(tag[atag])
        #result = sorted(result.iteritems(),key=itemgetter(1),reverse=True)
        '''    
        tag_set = set([])
        for (w,s) in keyword:
            if w in word_tag:
                atag = word_tag[w]
                for aatag in atag:
                    tag_set.add(aatag)

        for aatag in tag_set:
            result[aatag] = 1.0
        
        for (w,s) in keyword:
            if w in word_tag:
                atag = word_tag[w]
                for aatag in tag_set:
                    if aatag in atag:
                        result[aatag] *= atag[aatag]/tag[aatag]
                    else:
                        result[aatag] *= 0.1

        for atag in result:
            result[atag] *= tag[atag]
            
        result = sorted(result.iteritems(),key=itemgetter(1),reverse=True)
        '''
                        
        if len(result) >5:
            result = result[:5]
        if len(result) == 0:
            rs = "java python php"
        else:
            rs = ""
            for (w,t) in result:
                rs += (" "+w)
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
