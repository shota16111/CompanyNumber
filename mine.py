'''
2022/11/5~
海外法人企業数可視化
'''


import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter('ignore')

# 日本語の列情報が含まれているためencordingを指定する
df_all_rate = pd.read_csv(
    './CSV/CSV_data/全産業_国・地域別_増減率.csv', encoding='shift_jis')
df_all = pd.read_csv('./CSV/CSV_data/全産業_国・地域別.csv', encoding='shift_jis')
df_large_rate = pd.read_csv(
    './CSV/CSV_data/大分類_国・地域別_増減率.csv', encoding='shift_jis')
df_large = pd.read_csv('./CSV/CSV_data/大分類_国・地域別.csv', encoding='shift_jis')
df_midle_rate = pd.read_csv(
    './CSV/CSV_data/中分類_国・地域別_増減率.csv', encoding='shift_jis')
df_midle = pd.read_csv('./CSV/CSV_data/中分類_国・地域別.csv', encoding='shift_jis')

st.title('日本企業の海外法人数')

# 緯度経度のCSVファイル
jp_lat_lon = pd.read_csv('pref_lat_lon.csv')
# 列名の名前変更
jp_lat_lon = jp_lat_lon.rename(columns={'pref_name': '都道府県名'})
df_all = df_all[(df_all['集計年'] == 2019)]
# 列(都道府県名 )を基準にデータフレームを結合している。緯度経度情報をデータフレームに加えている。
df_all = pd.merge(df_all, jp_lat_lon, on='都道府県名')


prefecture_list = df_all['都道府県名'].unique()
company_sum = {}
for prefecture in prefecture_list:
    df_prefecture = df_all[(df_all['都道府県名'] == prefecture)]
    num = df_prefecture['現地法人企業数（社）']
    company_sum[prefecture] = num.sum()

list_prefecture = []
list_sum = []
for k, v in company_sum.items():
    list_prefecture.append(k)
    list_sum.append(v)

dict1 = dict(Prefecture=list_prefecture, CompanyNum=list_sum)
dataframe_ex = pd.DataFrame(data=dict1)


dataframe_ex = dataframe_ex.rename(columns={'Prefecture': '都道府県名'})
dataframe_ex = dataframe_ex.rename(columns={'CompanyNum': '現地法人企業数の合計'})

df_pref_map = pd.merge(dataframe_ex, jp_lat_lon, on='都道府県名')
company_num_sum = df_pref_map['現地法人企業数の合計']

# 正規化。最大1。最小値0
df_pref_map['現地法人企業数の合計'] = (df_pref_map['現地法人企業数の合計']-df_pref_map['現地法人企業数の合計'].min())/(
    df_pref_map['現地法人企業数の合計'].max()-df_pref_map['現地法人企業数の合計'].min())


view = pdk.ViewState(longitude=139.691648,
                     latitude=35.689185,
                     zoom=4,
                     pitch=40.5,)


layer = pdk.Layer("HeatmapLayer",
                  data=df_pref_map,
                  opacity=0.8,
                  get_position=["lon", "lat"],
                  threshold=0.3,
                  get_weight='現地法人企業数の合計'

                  )

layer_map = pdk.Deck(layers=layer, initial_view_state=view)
st.pydeck_chart(layer_map)

show_df = st.checkbox('show data frame')
if show_df == True:
    df_pref_map['現地法人企業数の合計'] = company_num_sum
    st.write(df_pref_map)

# 集計年別の一人当たりの平均賃金の推移をグラフで表示
'''

「出典：RESAS（地域経済分析システム）」

「本結果はRESAS（地域経済分析システム）を加工して作成しております。」
'''
