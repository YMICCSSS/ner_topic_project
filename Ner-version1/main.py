import kashgari
from kashgari.tasks.labeling import BiLSTM_CRF_Model
from kashgari.embeddings import BERTEmbedding
import codecs
import csv
import pandas as pd
from opencc import OpenCC
import ast
from kashgari.tasks.labeling.base_model import BaseLabelingModel

#資料處理成我要的格式
# my_trainx =[]
# with codecs.open("comment.csv","r",encoding="utf-8") as f:
#     rows = csv.reader(f)
#     for i in rows:
#         xx = []
#         for w in i[0]:
#             xx.append(w)
#         my_trainx.append(xx)
# print(len(my_trainx))

#引入問題跟答案
df_sen = pd.read_csv("result_2.csv",encoding="utf-8")

#建立問題與答案list
all_ans = []
all_sen = []
aspectTerm_t = []
for i in range(df_sen.shape[0]):
    a = str(df_sen.loc[i, "dish"]).split("?")
    s = str(df_sen.loc[i, "text"])
    # t = str(df_sen.loc[i,"ans"]).split("?")
    one_ans = []
    #  <aspectTerm> : from="4" polarity="positive" term="food" to="8"
    aspectTerm_i = []
    for i in range(len(s)):
        one_ans = one_ans + ["O"]
    # print(s)
    # print(a)
    for j in a:
        try:
            jj = j.split(",")
            j1 = jj[0]
            j2 = jj[1].replace(" a", "positive").replace("a豆干肉絲", "positive").replace("a", "positive").replace("b",
                                                                                                               "neutral").replace(
                "c", "negative")
        except:
            continue
        if j1 in s:
            j1_from = s.index(j1)
            j1_to = s.index(j1) + len(j1)
            aspectTerm_p = [j1, str(j1_from), str(j1_to), j2]
            # print(aspectTerm_p)
            aspectTerm_i = aspectTerm_i + [aspectTerm_p]
            one_ans[j1_from] = "B-1"
            for x in range(len(j1) - 1):
                one_ans[s.index(j1) + x + 1] = "I-1"
    all_ans = all_ans + [one_ans]
    all_sen = all_sen + [s]
    # print(one_ans)

    aspectTerm_t = aspectTerm_t + [aspectTerm_i]

all_sen_1 = []
for all in range(len(all_sen)):
    y=[]
    for i in all_sen[all]:
        y.append(i)
    all_sen_1.append(y)

# 將問題從繁體轉簡體
# all_sen_1 = str(all_sen_1)
# cc = OpenCC('t2s.json')
# all_sen_1 = cc.convert(all_sen_1)
# all_sen_1  = ast.literal_eval(all_sen_1 )

#all_sen_1 =問題,all_ans=答案
print(all_sen_1)
print(all_ans)

train_x =all_sen_1[0:2500]
train_y =all_ans[0:2500]
valid_x =all_sen_1[2501:2700]
valid_y =all_ans[2501:2700]
test_x =all_sen_1[2701:2876]
test_y =all_ans[2701:2876]

#設定一層embedding，bert育訓練模型會給進去的每一個詞一個index及向量(包含位置向量?),每一批次訓練會丟最多128個字進去訓練
#所以書輸出最多也128個字

#使用哈工大讯飞联合实验室发布小参数量预训练模型RBT3
bert_embed = BERTEmbedding('electra',
                           task=kashgari.LABELING,
                           sequence_length=128)


from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.python import keras
from kashgari.callbacks import EvalCallBack
#patience=3是看每一個epoch
stop_callback = EarlyStopping(patience=3, restore_best_weights=True)
save_callback = ModelCheckpoint("5_29_1", save_best_only=True)



model = BiLSTM_CRF_Model(bert_embed)
model.fit(train_x,
          train_y,
          x_validate=valid_x,
          y_validate=valid_y,
          callbacks=[stop_callback, save_callback],
          batch_size=250,
          epochs=25)


# 验证模型，此方法将打印出详细的验证报告
model.evaluate(test_x, test_y)

# 保存模型到 `model_name` 目录下
model.save('5_29_1')

# 加载保存模型
loaded_model = kashgari.utils.load_model('5_29_1')

# 使用模型进行预测
loaded_model.predict(test_x[:100])




# print(len(all_sen), len(aspectTerm_t), len(all_ans))
# # 存成txt檔
# with open("/content/drive/My Drive/tibame/ans.txt","w") as f:
#         f.write(str(all_ans))
# with open("/content/drive/My Drive/tibame/sen.txt","w") as f:
#         f.write(str(all_sen))
