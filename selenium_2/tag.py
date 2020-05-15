import pandas as pd
import glob
import os
import numpy as np

save_num = 50 # 每標記幾筆就先存檔，避免意外發生QQ
def save_csv(df):
	if choose == 't':
		series_tag = pd.Series(lst_tag).astype(str) # 預設空的Series Type會是float64，要手動指定為str
		series_dish = pd.Series(lst_dish).astype(str) 
		df['tag'] = series_tag
		df['dish'] = series_dish
	newpath = path + name + '_tag.csv'
	df.to_csv(newpath, index=False, encoding="utf-8")

def tag(df):
	curr_count = ''
	if choose == 't':
		for index, row in df.iterrows():# id,name,date,star,text
			curr_count = str(row['id']) + '/' + str(len(df.index))
			print('\n', curr_count, row['text'])
			lst_tag.append(input('請標記情緒(a正面，b中性，c負):'))
			lst_dish.append(input('請標記菜名(菜,情緒，每道菜依?隔開):'))

			if (row['id'] % save_num == 0):
				print('每', save_num, '筆先存檔')
				save_csv(df)
		# print(df.dtypes)
	elif choose == 'c':
		df['tag'] = df['tag'].astype(str)  # 預設空的Series Type會是float64，要手動指定為str
		df['dish'] = df['dish'].astype(str)
		for index, row in df.iterrows():# id,name,date,star,text,dish,tag
			curr_count = str(row['id']) + '/' + str(len(df.index))
			show_tag = '【' + str(row['tag']) + '】'
			show_dish = '【' + str(row['dish']) + '】'
			print('\n', curr_count , row['text'], show_tag, show_dish)
			newtag = input('更新情緒(不更新按enter跳過):')
			if newtag != '':
				if newtag == 'n':
					df.at[index, 'tag'] = np.nan
				else:
					df.at[index, 'tag'] = newtag

			newdish = input('更新菜名(不更新按enter跳過,空值輸入n):')
			if newdish != '':
				if newdish == 'n':
					df.at[index, 'dish'] = np.nan
				else:
					df.at[index, 'dish'] = newdish
			if (row['id'] % save_num == 0):
				print('每', save_num, '筆先存檔')
				save_csv(df)

district = input('請輸入你的行政區:')
choose = input('請選擇要 t標記 or c檢查:')
path = './csv/熱炒/台北市/' + district + '/'
files = []

if choose == 't':
	files = glob.glob(path+'*_review.csv')
elif choose == 'c':
	files = glob.glob(path+'*_tag.csv')
else:
	os._exit(0)

store_count = len(files)
for i in range(store_count):
	file = files[i]
	name = os.path.basename(file).split('_')[0]
	df = pd.read_csv(file, encoding='utf8', engine='python')
	lst_dish = []
	lst_tag = []
	print('======', str(i+1) + '/' + str(store_count), name, ',評論總共有', len(df.index), '筆 ======', end='  >>>')
	ans = input('繼續標註? q離開 n換下一家店：')

	if ans  == 'q':
		break
	elif ans == 'n':
		continue
	if len(df.index) == 0:
		print('這家店:', name, ',完全沒有評論，換下一家店')
		continue
	
	# print(df.dtypes)
	tag(df)
	save_csv(df)
	print(df)
	print('============ 這家店標記完成 ============')
