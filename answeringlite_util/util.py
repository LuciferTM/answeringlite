# -*- coding:utf-8 -*-
import os
import jieba
from gensim import corpora, models, similarities

def cleanFileByDir(bfile_path, rfile_path, cfile_path):
    '''
    :param bfile_path:
    :param rfile_path:
    :param cfile_path:
    :return:
    '''
    fnamelist = os.listdir(rfile_path)
    for fname in fnamelist:
        if fname.find(".txt") > 0:
            rawfile = open(rfile_path + "/" + fname)
            fi = 0
            cleanfile = open(bfile_path + "/" + cfile_path + "/" + fname, "w")
            for line in rawfile.readlines():
                line = line.strip()
                vchar = 0
                for ch in line:
                    if ch == "\n":
                         continue
                    elif ch == "\r":
                         continue
                    elif ch == "\t":
                         continue
                    elif ch == " ":
                         continue
                    elif ch == "\b":
                         continue
                    elif ch == "\v":
                         continue
                    elif ch == "\e":
                         continue
                    elif ch == "\0":
                         continue
                    elif ch == "\f":
                         continue
                    else:
                        vchar = 1
                        break

                if vchar == 0:
                    continue
                elif line.find("<h2>") == -1 and line.find("#p#") == -1 and line.find(".........") == -1:
                    if len(line) < 10:
                        cleanfile.write(line)
                    else:
                        cleanfile.write(line + "\n")
            rawfile.close()
            cleanfile.close()

def cleanFile(file_path, cfile_path):
    '''
    :param file_path:
    :param cfile_path:
    :return:
    '''

    (filepath, filename) = os.path.split(file_path)
    if filename.find(".txt") > 0:
        rawfile = open(file_path)
        fi = 0
        cleanfile = open(cfile_path + "/" + filename, "w")
        for line in rawfile.readlines():
            line = line.strip()
            vchar = 0
            for ch in line:
                if ch == "\n":
                     continue
                elif ch == "\r":
                     continue
                elif ch == "\t":
                     continue
                elif ch == " ":
                     continue
                elif ch == "\b":
                     continue
                elif ch == "\v":
                     continue
                elif ch == "\e":
                     continue
                elif ch == "\0":
                     continue
                elif ch == "\f":
                     continue
                else:
                    vchar = 1
                    break

            if vchar == 0:
                continue
            elif line.find("<h2>") == -1 and line.find("#p#") == -1 and line.find(".........") == -1:
                if len(line) < 10:
                    cleanfile.write(line)
                else:
                    cleanfile.write(line + "\n")
        rawfile.close()
        cleanfile.close()

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
        sentenceNum = sentenceNum + lines[i].count(".") + lines[i].count("?") + lines[i].count("!") + \
                      lines[i].count("。") + lines[i].count("？") + lines[i].count("！") + 1
        i = i + 1
    if i == len(lines):
        fraglist = head + "[" + docName + "]"
        txtfile.close()
        return fraglist
    else:
        sentenceNum = 0

    while i < len(lines) :
        # 判断句数，合并
        tail = tail + lines[i]
        sentenceNum = sentenceNum + lines[i].count(".") + lines[i].count("?") + lines[i].count("!") + \
                      lines[i].count("。") + lines[i].count("？") + lines[i].count("！") + 1

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

def preparedoc(cleanfilepath):
    documents = []
    fragment = []
    cfilenamelist = os.listdir(cleanfilepath) #BASEFILE_PATH + "/" + CLEANFILE_PATH
    for cfilename in cfilenamelist:
        if cfilename.find(".txt") > 0:
            documents = documents + [fragment for fragment in txtfrag(8, cleanfilepath + "/" + cfilename)]

    return documents

# TODO: 查询
def query(dictfilename, mmfilename, question, stoplist, indexfilename, documents, modelfilename, ldamodelfilename, ldaindexfilename):
    dictionary = corpora.Dictionary.load(dictfilename)
    corpus = corpora.MmCorpus(mmfilename)

    print(dictionary)

    tfidf = models.TfidfModel.load(modelfilename)
    lda = models.LdaModel.load(ldamodelfilename)

    # print("\nTopic List: \n{}\n".format(lda.show_topics()))

    query = []

    seg_list = jieba.cut_for_search(question)
    doctext = " ".join(seg_list)
    query = [word for word in doctext.split() if word not in stoplist]
    # print(query)
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
