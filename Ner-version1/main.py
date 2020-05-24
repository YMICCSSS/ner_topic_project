from kashgari.corpus import ChineseDailyNerCorpus
import kashgari
from kashgari.tasks.labeling import BiLSTM_CRF_Model
from kashgari.embeddings import BERTEmbedding
import codecs
import csv
import pandas as pd
from opencc import OpenCC
import ast


my_trainx =[]
with codecs.open("comment.csv","r",encoding="utf-8") as f:
    rows = csv.reader(f)
    for i in rows:
        xx = []
        for w in i[0]:
            xx.append(w)
        my_trainx.append(xx)
print(len(my_trainx))


df_sen = pd.read_csv("sen_d.csv",encoding="utf-8")

all_ans = []
all_sen = []
aspectTerm_t = []
for i in range(df_sen.shape[0]):
    a = str(df_sen.loc[i, "ans"]).split("?")
    s = str(df_sen.loc[i, "sentence"])
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
            one_ans[j1_from] = "B"
            for x in range(len(j1) - 1):
                one_ans[s.index(j1) + x + 1] = "I"
    all_ans = all_ans + [one_ans]
    all_sen = all_sen + [s]
    # print(one_ans)

    aspectTerm_t = aspectTerm_t + [aspectTerm_i]

    # print("=========================")
print(all_ans)
print(my_trainx)
my_trainx = str(my_trainx)
cc = OpenCC('t2s.json')  # 繁體轉簡體
# can also set conversion by calling set_conversion

my_trainx = cc.convert(my_trainx)
my_trainx  = ast.literal_eval(my_trainx )

print(my_trainx)

train_x =my_trainx[0:500]
train_y =all_ans[0:500]
valid_x =my_trainx[501:550]
valid_y =all_ans[501:550]
test_x =my_trainx[551:707]
test_y =all_ans[551:707]

bert_embed = BERTEmbedding('chinese_wwm_ext_L-12_H-768_A-12',
                           task=kashgari.LABELING,
                           sequence_length=20)


from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
stop_callback = EarlyStopping(patience=3, restore_best_weights=True)
save_callback = ModelCheckpoint("fashion.h5", save_best_only=True)

model = BiLSTM_CRF_Model(bert_embed)
model.fit(train_x,
          train_y,
          valid_x,
          valid_y,
callbacks=[stop_callback, save_callback],
          batch_size=30,
          epochs=5)


# 验证模型，此方法将打印出详细的验证报告
model.evaluate(test_x, test_y,batch_size=20)

# 保存模型到 `saved_ner_model` 目录下
model.save('saved_ner_model')

# 加载保存模型
loaded_model = kashgari.utils.load_model('saved_ner_model')

# 使用模型进行预测
loaded_model.predict(test_x[:10])




# print(len(all_sen), len(aspectTerm_t), len(all_ans))
# # 存成txt檔
# with open("/content/drive/My Drive/tibame/ans.txt","w") as f:
#         f.write(str(all_ans))
# with open("/content/drive/My Drive/tibame/sen.txt","w") as f:
#         f.write(str(all_sen))
