#coding: utf-8
'''
这个文件提供一个简单的接口，给大家使用parse
'''
#使用了textblob 工具包，如果报错，请访问这个连接 https://github.com/sloria/TextBlob
from textblob import TextBlob as tb
import textblob
import nltk
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
import re

#suffix_str = ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']
suffix_str = ['s','ies','ment','ious','.',',','...',"'s"]
#suffix_str = ['s']
porter = nltk.PorterStemmer()
#这个是比较轻的stem
def small_stem(word):
    #for suffix in 
    for suffix in suffix_str:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word
#去掉所有的非字母的字母
def remove_non_chap(word):
    if word.isdigit()==False:
        return word
    else:
        return 'isnumber'
    
class nlp:
    def __init__(self):
        self.tb = tb
        self.porter = nltk.PorterStemmer()
        self.tk = TreebankWordTokenizer()
        self.stopwords = set(stopwords.words())
    def tag(self,text):
        blob = self.tb(text)
        return blob.tags
    #clean是词干化和标点符号的
    def noun(self,text,clean=True):
        text = text.replace('\\n',' ')
        text = text.replace('\\t',' ')
        blob = self.tb(text)
        tags = blob.tags
        result = []
        for (aword,atag) in tags:
            if atag == "NNP" or atag == "NNS" or atag == "NN":
                result.append(aword.lower())

        if clean == True:
            clean_result = []
            for word in result:
                nword = porter.stem(remove_non_chap(word))
                #nword = small_stem(remove_non_chap(word))
                if len(nword) > 2:
                    clean_result.append(nword)
            return clean_result
        return result

    def in_stop(self,word):
        return word in in_stop    
    def edit_distance(self,word1, word2):
        matrixTable = [[i for i in range(len(word2)+1)] for j in range(len(word1)+1)]

        for i in range(len(word1)+1):
            matrixTable[i][0] = i
  
        for i in range(1, len(word1)+1):
            for j in range(1, len(word2)+1):
                top = matrixTable[i-1][j] + 1
                left = matrixTable[i][j-1] + 1
                if word1[i-1:i] == word2[j-1:j]:
                    topLeft = matrixTable[i-1][j-1]
                else:
                    topLeft = matrixTable[i-1][j-1] + 1
                matrixTable[i][j] = min(top, left, topLeft)


        return matrixTable[len(word1)][len(word2)]
                
    #这个东西可能用着不太好，暂时先别用
    def noun_p(self,text):
        blob = self.tb(text)
        return blob.noun_phrases

    def title_tokenize(self,s):
        return [token for token in re.findall(r'\b\w[\w#+.-]*(?<!\.$)', s.lower()) if token not in self.stopwords and len(token)<30]
        
    def token(self,text):
        result,clean_result = self.tk.tokenize(text),[]
        for word in result:
            nword = word.lower()
            #nword = small_stem(nword)
            if len(nword) <= 30:
                clean_result.append(nword)
        return clean_result

    def bigrams(self,text):
        return nltk.bigrams(text)

    def little_stem(self,word):
        return small_stem(word)
        
if __name__ == '__main__':
    print "this is test case"
    mn = nlp()
    sent = "what's your mother's name?"
    a = '''
    Technology Need,"Each day we start our instruction with literacy. The students love to read non-fiction. They frequently ask to research what they have been reading. In our second grade class, I have 19 students....,My students need an iPad with a case and screen protector for the classroom.,"Each day we start our instruction with literacy. The students love to read non-fiction. They frequently ask to research\nIn our second grade class, I have 19 students. They are very energetic and always enjoy using technology in the classroom. Some students have opportunities to use technology at home but many do not. Our school is small and very rural. Our\nThe students would love to have an iPad mini with a case and screen protector to read, do learning activities, and research topics. We currently do not have an iPad in our classroom. We have two working computers and the more technology t\nThis technology will enhance the learning of the students in my classroom everyday. They will get to use this iPad mini to read, do learning activities, and research topics. Right now, it is hard for all of them to get to use the computer. I will be able to assign each student time weekly to further their instruction. 
    '''
    print mn.token(a)
    print mn.edit_distance("coreplot","core-plot")
