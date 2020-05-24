# from kashgari.corpus import ChineseDailyNerCorpus
# import kashgari
# from kashgari.tasks.labeling import BiLSTM_CRF_Model
# from kashgari.embeddings import BERTEmbedding
# import codecs
# import csv
# import pandas as pd
# from opencc import OpenCC
# import ast
#
# # train_x, train_y = ChineseDailyNerCorpus.load_data('train')
# # # valid_x, valid_y = ChineseDailyNerCorpus.load_data('valid')
# # # test_x, test_y = ChineseDailyNerCorpus.load_data('test')
# # print(train_x[0])
# # print(train_y[0])
# # print(type(train_y))
# # print(type(train_y[0]))
#
# my_trainx =[]
# with codecs.open("comment.csv","r",encoding="utf-8") as f:
#     rows = csv.reader(f)
#     for i in rows:
#         xx = []
#         for w in i[0]:
#             xx.append(w)
#         my_trainx.append(xx)
# print(len(my_trainx))
#
#
# # with codecs.open("ans3.txt","r",encoding="utf-8") as f:
# #     rows = f.readlines()
# #     for i in rows:
# #         print(i)
# #         x = ast.literal_eval(i)
# #         print(x)
# #         print(type(x))
# #
#     # print(rows)
#     # for i in rows:
#     #     print(i)
#     #     # i =["['O', 'O', 'O', 'B', 'O', 'O', 'O']"]
#     #     xx = []
#     #     print(list(i))
#     #     i = ast.literal_eval(i)
#     #     print(i)
#         # for w in i[0]:
#         #     print(w)
# #             xx.append(w)
# #         my_trainy.append(xx)
# # print(len(my_trainy))
#
#
# # i = ast.literal_eval(i)
# # print(i)
# # print(type(i))
#
# # x = ast.literal_eval(﻿x)
#
# # all_ans= []
# # for i in range(df_sen.shape[0]):
# #     all_ans = all_ans + list(df_sen.loc[i,"ans"])
# # print(all_ans)
#
#
# df_sen = pd.read_csv("sen_d.csv",encoding="utf-8")
#
# all_ans = []
# all_sen = []
# aspectTerm_t = []
# for i in range(df_sen.shape[0]):
#     a = str(df_sen.loc[i, "ans"]).split("?")
#     s = str(df_sen.loc[i, "sentence"])
#     # t = str(df_sen.loc[i,"ans"]).split("?")
#     one_ans = []
#     #  <aspectTerm> : from="4" polarity="positive" term="food" to="8"
#     aspectTerm_i = []
#     for i in range(len(s)):
#         one_ans = one_ans + ["O"]
#     # print(s)
#     # print(a)
#     for j in a:
#         try:
#             jj = j.split(",")
#             j1 = jj[0]
#             j2 = jj[1].replace(" a", "positive").replace("a豆干肉絲", "positive").replace("a", "positive").replace("b",
#                                                                                                                "neutral").replace(
#                 "c", "negative")
#         except:
#             continue
#         if j1 in s:
#             j1_from = s.index(j1)
#             j1_to = s.index(j1) + len(j1)
#             aspectTerm_p = [j1, str(j1_from), str(j1_to), j2]
#             # print(aspectTerm_p)
#             aspectTerm_i = aspectTerm_i + [aspectTerm_p]
#             one_ans[j1_from] = "B"
#             for x in range(len(j1) - 1):
#                 one_ans[s.index(j1) + x + 1] = "I"
#     all_ans = all_ans + [one_ans]
#     all_sen = all_sen + [s]
#     # print(one_ans)
#
#     aspectTerm_t = aspectTerm_t + [aspectTerm_i]
#
#     # print("=========================")
# print(all_ans)
# print(my_trainx)
# my_trainx = str(my_trainx)
# cc = OpenCC('t2s.json')  # convert from Simplified Chinese to Traditional Chinese
# # can also set conversion by calling set_conversion
# # cc.set_conversion('s2tw')
# my_trainx = cc.convert(my_trainx)
# my_trainx  = ast.literal_eval(my_trainx )
#
# print(my_trainx)
#
# train_x =my_trainx[0:500]
# train_y =all_ans[0:500]
# valid_x =my_trainx[501:550]
# valid_y =all_ans[501:550]
# test_x =my_trainx[551:707]
# test_y =all_ans[551:707]
# # 使用模型进行预测
#
# loaded_model = kashgari.utils.load_model('saved_ner_model')
#
# loaded_model.predict(test_x[:10])
# -*- coding: utf-8 -*-
import kashgari
import re

loaded_model = kashgari.utils.load_model('saved_ner_model')


def cut_text(text, lenth):
    textArr = re.findall('.{' + str(lenth) + '}', text)
    textArr.append(text[(len(textArr) * lenth):])
    return textArr


def extract_labels(text, ners):
    ner_reg_list = []
    if ners:
        new_ners = []
        for ner in ners:
            new_ners += ner;
        for word, tag in zip([char for char in text], new_ners):
            if tag != 'O':
                ner_reg_list.append((word, tag))

    # 输出模型的NER识别结果
    labels = {}
    if ner_reg_list:
        for i, item in enumerate(ner_reg_list):
            if item[1].startswith('B'):
                label = ""
                end = i + 1
                while end <= len(ner_reg_list) - 1 and ner_reg_list[end][1].startswith('I'):
                    end += 1

                ner_type = item[1].split('-')[1]

                if ner_type not in labels.keys():
                    labels[ner_type] = []

                label += ''.join([item[0] for item in ner_reg_list[i:end]])
                labels[ner_type].append(label)

    return labels


while True:
    text_input = input('sentence: ')

    texts = cut_text(text_input, 100)
    ners = loaded_model.predict([[char for char in text] for text in texts])
    print(ners)
    # labels = extract_labels(text_input, ners)
    # print(labels)
