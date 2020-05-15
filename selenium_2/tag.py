import pandas as pd
import glob
import os

def tag(df):
	if choose == 't':
		for index, row in df.iterrows():# id,name,date,star,text
			print('\n', str(row['id']) + '/' + str(len(df.index)), row['text'])
			lst_tag.append(input('請標記情緒(a正面，b中性，c負):'))
			lst_dish.append(input('請標記菜名(菜,情緒，每道菜依?隔開):'))
		series_dish = pd.Series(lst_dish)
		series_tag = pd.Series(lst_tag)
		df['tag'] = series_tag
		df['dish'] = series_dish
	elif choose == 'c':
		for index, row in df.iterrows():# id,name,date,star,text,dish,tag
			print('\n', str(row['id']) + '/' + str(len(df.index)), row['text'], row['tag'], row['dish'])
			newtag = input('更新情緒(不更新按enter跳過):')
			if newtag != '':
				if newtag == 'n':
					df.at[index, 'tag'] = None
				else:
					df.at[index, 'tag'] = newtag

			newdish = input('更新菜名(不更新按enter跳過,空值輸入n):')
			if newdish != '':
				if newdish == 'n':
					df.at[index, 'dish'] = None
				else:
					df.at[index, 'dish'] = newdish

district = input('請輸入你的行政區:')
choose = input('請選擇要 t標記 or c檢查:')
path = './csv/熱炒/台北市/' + district + '/'
files = []

if choose == 't':
	files = glob.glob(path+'*_review.csv')
elif choose == 'c':
	files = glob.glob(path+'*_tag.csv')
else:
	os.exit()

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
	tag(df)

	print('============ 這家店標記完成 ============')
	print(df)
	newpath = path + name + '_tag.csv'
	df.to_csv(newpath, index=False, encoding="utf-8")