
# coding: utf-8

# In[128]:

import logging, os
from gensim import corpora, models, similarities
#import thulac
import jieba
from gensim.summarization import summarize, keywords

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

logging.disable(logging.INFO)

BASEFILE_PATH = "answeringlite"
RAWFILE_PATH = BASEFILE_PATH
CLEANFILE_PATH = "cleaned"
# TODO: 批量清洗文件，针对百科特殊情况，不必须
def cleanFile(bfile_path, rfile_path, cfile_path):
    fnamelist = os.listdir(rfile_path)

    for fname in fnamelist:
        if fname.find(".txt") > 0:
            rawfile = open(rfile_path + "/" + fname)
            fi = 0
            cleanfile = open(bfile_path + "/" + cfile_path + "/" + fname, "w")
            
            #ii = 0
            for line in rawfile.readlines():
                line = line.strip()
                #print("Line {}: ******* {} ******\n{}".format(ii, len(line), line))
                vchar = 0
                for ch in line:
        
                    if ch == "\n":
                    #    print("blank char: n")
                         continue
                    elif ch == "\r":
                    #    print("blank char: r")
                         continue
                    elif ch == "\t":
                    #    print("blank char: t")
                         continue
                    elif ch == " ":
                    #    print("blank char: blank")
                         continue
                    elif ch == "\b":
                    #    print("blank char: b")
                         continue
                    elif ch == "\v":
                    #    print("blank char: v")
                         continue
                    elif ch == "\e":
                    #    print("blank char: e")
                         continue
                    elif ch == "\0":
                    #    print("blank char: 0")
                         continue
                    elif ch == "\f":
                    #    print("blank char: f")
                         continue
                    else:
                        vchar = 1
                        break
                    
                if vchar == 0:
                    #print("blank line")
                    #ii += 1
                    continue
                elif line.find("<h2>") == -1 and line.find("#p#") == -1 and line.find(".........") == -1:
                    #print("Add #{}: {}".format(ii, line))
                    # if too short text
                    if len(line) < 10:
                        cleanfile.write(line)
                    else:
                        cleanfile.write(line + "\n")
                    #ii += 1
                

            rawfile.close()
            cleanfile.close()
# 为了调试的速度暂时去掉
#cleanFile(BASEFILE_PATH, RAWFILE_PATH, CLEANFILE_PATH)

# TODO: 文件分片
def txtfrag(blockLen, docName):
    
    if blockLen < 1:
        raise Exception("最小分片不能小于1")
        
    txtfile = open(docName)
    
    lines = txtfile.readlines()
    fraglist = []
    i = 0
    head = ""
    tail = ""
    sentenceNum = 0
    sentences = []
    
    # 初始化head
    while i < len(lines) and sentenceNum < blockLen :
        # 判断句数，合并
        head = head + lines[i]
        sentenceNum = sentenceNum + lines[i].count(".") +                       lines[i].count("?") + lines[i].count("!") +                       lines[i].count("。") + lines[i].count("？") + lines[i].count("！") + 1
        
        i = i + 1
    
    if i == len(lines):
        fraglist = head + "[" + docName + "]"
        #logging.debug("sentenceNum = {} head returned: {}".format(sentenceNum, fraglist))
        txtfile.close()
        
        return fraglist
    else:
        sentenceNum = 0

    while i < len(lines) :
        # 判断句数，合并
        tail = tail + lines[i]
        sentenceNum = sentenceNum + lines[i].count(".") +                       lines[i].count("?") + lines[i].count("!") +                       lines[i].count("。") + lines[i].count("？") + lines[i].count("！") + 1
        
        #logging.debug("sNUm = {} tail: {}".format(sentenceNum, tail))

        if sentenceNum < blockLen:
            i = i + 1
        else:
            # 生成head和tail
            #logging.debug("head: {}; tail: {}\n".format(head, tail))
            fraglist.append(head + tail + "[" + docName + "]")
            #fraglist.append(tail)
            i = i + 1

            head = tail
            tail = ""

            sentenceNum = 0

    # 剩余部分不足5句则与上一段合并
    if sentenceNum <= blockLen:
        #logging.debug("fraglist tail: {}".format(tail))
        if len(fraglist) > 0:
            fraglist[len(fraglist)-1] = fraglist[len(fraglist)-1] + tail
        else:
            fraglist = [tail + "[" + docName + "]"]
    
    txtfile.close()
    
    return fraglist

# TODO: 生成字典和索引
swfile = open("stopwords_lite.txt")
stoplist = [line.strip() for line in swfile.readlines()]
swfile.close()

def preparedoc(cleanfilepath):
    documents = []
    fragment = []
    cfilenamelist = os.listdir(cleanfilepath) #BASEFILE_PATH + "/" + CLEANFILE_PATH
    for cfilename in cfilenamelist:
        if cfilename.find(".txt") > 0:  
            documents = documents + [fragment for fragment in txtfrag(8, cleanfilepath + "/" + cfilename)]

    return documents

doclist = preparedoc(BASEFILE_PATH + "/" + CLEANFILE_PATH)

def indexing(documents, slist, dictfilename, mmfilename, indexfilename, modelfilename, ldamodelfilename, indexLDAfilename):
    #tlac = thulac.thulac(seg_only = True)
    texts = []

    for docfrag in documents:
        
        #doctext = tlac.cut(docfrag.strip(), text = True)
        seg_list = jieba.cut_for_search(docfrag.strip())
        doctext = " ".join(seg_list)
    
        text = [word for word in doctext.split() if word not in slist]

        texts.append(text)

    dictionary = corpora.Dictionary(texts)
    # from web，去掉极端词汇
    #dictionary.filter_extremes(no_below=1,no_above=1,keep_n=None)
    dictionary.save(dictfilename)
    #BASEFILE_PATH + "/" + "baike.dict"

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(mmfilename, corpus)
    #BASEFILE_PATH + "/" + "baike.mm"
    
    tfidf = models.TfidfModel(corpus)
    tfidf.save(modelfilename)
    corpus_tfidf = tfidf[corpus]
    index = similarities.SparseMatrixSimilarity(corpus = corpus_tfidf, num_features = 500000)
    index.save(indexfilename)
    #BASEFILE_PATH + '/baike.index'

    lda = models.LdaModel(corpus = corpus, id2word = dictionary, num_topics = 50, passes = 10, iterations = 8000)
    lda.save(ldamodelfilename)
    corpus_lda = lda[corpus]
    #corpus_lda = lda[corpus_tfidf]
    indexLDA = similarities.SparseMatrixSimilarity(corpus = corpus_lda, num_features = 500000)
    indexLDA.save(indexLDAfilename)
    
#load indexing file
#indexing(doclist, stoplist, BASEFILE_PATH + "/" + "baike.dict", BASEFILE_PATH + "/" + "baike.mm", BASEFILE_PATH + '/baike.index', BASEFILE_PATH + '/baike.model', BASEFILE_PATH + '/baike.LDAmodel', BASEFILE_PATH + '/baike.LDAindex')

# TODO: 查询
def query(dictfilename, mmfilename, question, stoplist, indexfilename, documents, modelfilename, ldamodelfilename, ldaindexfilename):
    
    dictionary = corpora.Dictionary.load(dictfilename)
    corpus = corpora.MmCorpus(mmfilename)
    
    print(dictionary)

    tfidf = models.TfidfModel.load(modelfilename)
    lda = models.LdaModel.load(ldamodelfilename)
    
    #测试LDA
    #for i in range(50):
    #    print("topic_{}: {}".format(i, dictionary[lda.get_topic_terms(i)[0][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[1][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[2][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[3][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[4][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[5][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[6][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[7][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[8][0]] + " " \
    #                                + dictionary[lda.get_topic_terms(i)[9][0]]))
    print("\nTopic List: \n{}\n".format(lda.show_topics()))
    
    query = []

    #tlac = thulac.thulac(seg_only = True)
    #doctext = tlac.cut(question, text = True)
    seg_list = jieba.cut_for_search(question)
    doctext = " ".join(seg_list)
    #print(doctext)

    query = [word for word in doctext.split() if word not in stoplist]

    print(query)

    vec_bow = dictionary.doc2bow(query)
    #vec_lda = lda[vec_bow]
    vec_tfidf = tfidf[vec_bow]
    #vec_lda = lda[vec_tfidf]
    
    #print("lda vector: \n{}\n".format(vec_lda))
    print("tfidf_vector: \n{}\n".format(vec_tfidf))
    
    index = similarities.SparseMatrixSimilarity.load(indexfilename)
    #lda_index = similarities.SparseMatrixSimilarity.load(ldaindexfilename)
    
    print("tfidf: \n")
    sims = index[vec_tfidf]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    
    an = ""
    
    for i in range(3):
        print(sims[i])
        print(documents[sims[i][0]])
        
    
    print("\n****************** 结果 ******************\n\n")
    tfidf_recomm = ""
    recommFileName = ""
    if sims[0][1] > 0.25:
        # 推荐文章
        frag = documents[sims[0][0]]
        an = documents[sims[0][0]]
        recommark = frag.rfind("[")
        if recommark > 1:
            #print("mark at {}; len is {}; frag is {}".format(recommark, len(frag), frag))
            tfidf_recomm = frag[:recommark]
            recommFileName = frag[(recommark+1):(len(frag) - 1)]
            #print("推荐文章： {}\n".format(recommFileName))
    else:
        an = "没有合适的答案，我们会记录下来，稍后回复你~ 你可以先看看我们推荐的相关学习资料。"
        tfidf_recomm = question
   


    #print("lda: \n")
    #ldasims = lda_index[vec_lda]
    #ldasims = sorted(enumerate(ldasims), key=lambda item: -item[1])
    #for i in range(10):
        #print(ldasims[i])
        #print(documents[ldasims[i][0]])
        #if ldasims[i][1] > 0.3:
            # 推荐文章
            #frag = documents[ldasims[i][0]]
            #recommark = frag.rfind("[")
            #if recommark > 1:
                #print("mark at {}; len is {}; frag is {}".format(recommark, len(frag), frag))
                #recommFileName = frag[(recommark+1):(len(frag) - 1)]
                #print("推荐文章： {}".format(recommFileName))
                
    #利用TFIDF匹配结果进行LDA推荐   
    seg_list = jieba.cut_for_search(tfidf_recomm)
    doctext = " ".join(seg_list)
    query2 = [word for word in doctext.split() if word not in stoplist]
    #print(query2)
    
    vec_bow_lda2 = dictionary.doc2bow(query2)
    vec_lda2 = lda[vec_bow_lda2]
    
    lda2_index = similarities.SparseMatrixSimilarity.load(ldaindexfilename)
    lda2sims = lda2_index[vec_lda2]
    lda2sims = sorted(enumerate(lda2sims), key = lambda item: -item[1])
    recomm_set = {recommFileName}
    for i in range(20):
        if lda2sims[i][1] > 0.3:
            #推荐文章
            frag = documents[lda2sims[i][0]]
            #print(frag)
            recommark = frag.rfind("[")
            if recommark > 1:
                recommFileName = frag[(recommark + 1) : (len(frag) - 1)]
                recomm_set.add(recommFileName)
                #print("推荐文章：{}".format(recommFileName))
    for f in recomm_set:
        print("推荐文章：{}".format(f))
                
    return an

doc = "如何关闭手机查找功能" 
#"客户入店多长时间内必须有服务人员上前打招呼？"
#"防水标变红但是内部没有腐蚀可以保修吗"
#"手机防水标变色了还可以保修吗"
#"手机防水标出现变色但不是完全变红，手机内部没有腐蚀迹象或液体留存，可以保修吗" 
#"哪种情况是可以为用户进行保修的（无须考虑未提及条件）" 
#"怎么识别小米max前壳组件是仿品LCD"
#"非通话状态扬声器杂音扬声器播放音频、视频等场景怎么办？" 
#"小米手机6抓取Modem log 的命令是" 
#"用户反馈新买的小米手机6无法使用NFC-SIM卡" 
#"使用小米手机6播放音乐或玩游戏时，扬声器会有轻微杂音现象"
answer_frag = query(BASEFILE_PATH + "/" + "baike.dict", BASEFILE_PATH + "/" + "baike.mm", doc, stoplist, BASEFILE_PATH
        + '/baike.index',doclist, BASEFILE_PATH + '/baike.model',BASEFILE_PATH + '/baike.LDAmodel', BASEFILE_PATH + '/baike.LDAindex')
commentpos = answer_frag.rfind("[")
answer = "......\n" + answer_frag[:commentpos] + "......"
print("\n=================回答===================\n{}".format(answer))




# In[ ]:




# In[ ]:



