#coding: utf-8

#util
from read_conf import config
import csv
from optparse import OptionParser
import cPickle as pickle
import os
import re
from itertools import combinations

#rake
from rake import Rake
rake = Rake()

#nltk
import nltk
from nltk.util import clean_html
from nltk.util import clean_url

#nlp
from nlp import nlp
mnlp = nlp()

tag_re = re.compile(r"<p>(.+?)</p>",re.DOTALL)

dp = config("../conf/dp.conf")

#这个函数的作用是去重
#先读取title，然后和test的title相对比，看看有没有重的
def remove_duplicate():
    dup = open(dp["dup_test"],"w")
    other = open(dp["other_test"],"w")
    w_dup = csv.writer(dup)
    w_other = csv.writer(other)
    
    #读取训练文件
    print "给测试集去重复"
    f = open(dp["raw_train"])
    train = {}

    reader = csv.reader(f)

    a = 0
    for line in reader:
        train[line[1]] = line[3]

        if a % 10000 == 0:
            print a
        a += 1

    f = open(dp["raw_test"])
    reader = csv.reader(f)    
    a = 0
    for line in reader:
        if line[1] in train:
            write_string = [line[0],train[line[1]]]
            w_dup.writerow(write_string)
        else:
            w_other.writerow(line)
        if a % 10000 == 0:
            print "line number:",a

        a += 1

#将测试集所有的编号写入到文件中
def extract_id():
    f = open(dp["raw_test"])
    reader = csv.reader(f)
    result = []
    a = 0
    for line in reader:
        result.append(line[0])
        if a % 100000 == 0:
            print a
        a += 1
    t = open(dp["id"],"wb")
    pickle.dump(result,t,True)    

#得到测试集全部的编号
def load_id():
    f = open(dp["id"])
    test_id = pickle.load(f)
    return test_id

#生成最后结果
def gen_submission(ndup_test,comp=True):
    print "生成最后结果"
    print "载入test的所有id"
    test_id = load_id()
    
    t = open(dp["result"],"w")
    writer = csv.writer(t)

    print "载入所有duplicate"
    dup_test = load_dup()

    print "写入结果"
    for one_id in test_id:
        w = [one_id]
        if one_id in dup_test:
            w.append(dup_test[one_id])
        else:
            w.append(ndup_test[one_id])
        writer.writerow(w)

    t.close()

    if comp == True:
        print "删除原来的文件"
        os.system("rm %s"%(dp["comp"]))
        print "打压缩包"
        os.system("gzip %s"%(dp["result"]))

#去除html网页里面的代码<pre><code>
def get_context(text):
    cont = tag_re.findall(text)
    if len(cont) == 0:
        return " "
    else :
        return ' '.join(cont)

def remove_html(text):
    #取出html的tag和url
    return clean_html(text)
    
def remove_tag():
    print "去除html文件中的tag"
    print "去除训练集的tag"
    
    f = open(dp["raw_train"])
    t = open(dp["ntag_train"],"w")
    
    reader = csv.reader(f)
    writer = csv.writer(t)

    a = 0
    for line in reader:
        if a == 0:
            a += 1
            continue
        raw_title = line[1]
        raw_body = line[2]
        tid = line[0]
        atag = line[3]
        
        clean_title,clean_body = remove_html(raw_title),remove_html(get_context(raw_body))
        writer.writerow([tid,clean_title,clean_body,atag])
        a += 1
        if a % 10000 == 0:
            print a

    print "去除测试集中的tag"
    
    f = open(dp["other_test"])
    t = open(dp["ntag_test"],"w")
    
    reader = csv.reader(f)
    writer = csv.writer(t)

    a = 0
    for line in reader:
        raw_title = line[1]
        raw_body = line[2]
        tid = line[0]
        
        clean_title,clean_body = remove_html(raw_title),remove_html(get_context(raw_body))
        writer.writerow([tid,clean_title,clean_body])
        a += 1
        if a % 10000 == 0:
            print a

#这个函数用来测试rake算法，其实rake的效果也不是特别好            
def test_rake():
    f = open(dp["ntag_train"])
    reader = csv.reader(f)
    a = 0
    for line in reader:
        keywords = rake.run(line[2])
        #keywords = mnlp.noun(line[1])
        print line[22]
        print keywords
        print line[3]
        print 40*"="
        a += 1
        if a >= 10:
            break

#这个函数的作用是构造两个矩阵，用dict存储，作用是当到时候分类用
def word_matrix():
    vocab = load_testwords()
    
    #两个矩阵
    word_tag = {}
    tag = {}
    word_count = {}

    a = 0
    #先开train文件
    f = open(dp["ntag_train"])
    reader = csv.reader(f)
    for line in reader:
        title,atag = line[1],line[3]
        atag = atag.split()
        for aatag in atag:
            if aatag not in tag:
                tag[aatag] = 1
            else:
                tag[aatag] += 1

        #先提取关键词
        if len(title)!= 0:
            keyword1 = rake.run(title)
            for (w,t) in keyword1:
                if len(w) <= 3 or t == 0 or w not in vocab:
                    continue
                if w not in word_tag:
                    word_tag[w] = {}
                for aatag in atag:
                    if aatag not in word_tag[w]:
                        word_tag[w][aatag] = t
                    else:
                        word_tag[w][aatag] += t
                        
                if w not in word_count:
                    word_count[w] = t
                else:
                    word_count[w] += t
        a += 1
        if a%10000 == 0:
            print a

    print "写入文件"
    print "词表长度",len(word_tag)
    t = open(dp["word_tag"],"wb")
    pickle.dump(word_tag,t,True)
    t = open(dp["tag"],"wb")
    pickle.dump(tag,t,True)
    t = open(dp["word_count"],"wb")
    pickle.dump(word_count,t,True)

def extract_testwords():
    print "抽取测试集词表"    
    f = open(dp["ntag_test"])
    reader = csv.reader(f)

    vocab = []

    a = 0
    for line in reader:
        if len(line[1]) > 0:
            keyword = rake.run(line[1])
            keys = [w for (w,s) in keyword]
            vocab.extend(keys)

        a += 1
        if a%10000 == 0:
            print a

    vocab = set(vocab)
    print "词表大小",len(vocab)
    t = open(dp["test_vocab"],"wb")
    pickle.dump(vocab,t,True)

def load_testwords():
    f = open(dp["test_vocab"])
    
    vocab = pickle.load(f)
    print "词表大小",len(vocab)    
    return vocab

def extract_tagrel():
    #这个文件的目的是抽取tag和tag之间的关系

    result = {}
    
    f = open(dp["ntag_train"])
    reader = csv.reader(f)
    a = 0
    for line in reader:
        if a == 0:
            a += 1
            continue

        tags = line[-1].split()
        for source,target in combinations(tags,2):
            result.setdefault(source,{})
            result.setdefault(target,{})

            result[source].setdefault(target,0)
            result[target].setdefault(source,0)

            result[source][target] += 1
            result[target][source] += 1
            
        a += 1
        if a %10000 == 0:
            print a,len(result)

    #衡量置信度关系
    #我打算将所有的置信度求出来，然后平均
    #先把tag的数量load进来
    f = open(dp["tag"])
    all_tag = pickle.load(f)

    print "删除置信度比较低的tag，置信度阈值设为0.1"
    final = {}
    for source in result:
        final.setdefault(source,{})
        for target in result[source]:
            if result[source][target]*1.0/all_tag[source] >= 0.1:
                final[source][target] = result[source][target]*1.0/all_tag[source]

    result = final
                
    t = open(dp["tagrel"],"wb")
    pickle.dump(result,t,True)
    
def main(options):
    if options.task == "remove_dup":
        remove_duplicate()
    elif options.task == "extract_id":
        extract_id()
    elif options.task == "remove_tag":
        remove_tag()

    elif options.task == "test_rake":
        test_rake()
    elif options.task == "word_matrix":
        word_matrix()

    elif options.task == "extract_testwords":
        extract_testwords()

    elif options.task == "extract_tagrel":
        extract_tagrel()

#读入duplicate
def load_dup():
    f = open(dp["dup_test"])
    reader = csv.reader(f)
    result = {}
    a = 0
    for line in reader :
        result[line[0]] = line[1]
        if a % 100000 == 0:
            print a
        a += 1

    return result

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-t","--task",dest="task",action="store",\
                      help=u"选择你要干什么事",type="string")
    (options, args) = parser.parse_args()
    #执行判断
    print options
    main(options)


    
