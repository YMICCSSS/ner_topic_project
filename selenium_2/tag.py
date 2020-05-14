import pandas as pd
import glob
import os

district = input('請輸入你的行政區:')
path = './csv/熱炒/台北市/' + district + '/'

files = glob.glob(path+'*_review.csv')
store_count = len(files)

for i in range(store_count):
	file = files[i]
	# print(file)
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
	for index, row in df.iterrows():# id,name,date,star,text
		print('\n', str(row['id']) + '/' + str(len(df.index)), row['text'])
		lst_tag.append(input('請標記情緒(a正面，b中性，c負):'))
		lst_dish.append(input('請標記菜名(菜,情緒，每道菜依?隔開):'))

	series_dish = pd.Series(lst_dish)
	series_tag = pd.Series(lst_tag)
	df['dish'] = series_dish
	df['tag'] = series_tag
	print('============ 這家店標記完成 ============')
	print(df)
	newpath = path + name + '_tag.csv'
	df.to_csv(newpath, index=False, encoding="utf-8")