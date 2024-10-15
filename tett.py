import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

def get_info(search_str):
    url = f'https://search.books.com.tw/search/query/key/{search_str}/cat/all/fclick/autocmp-pc'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    data = [['書名', '作者', '價格', '折扣']]

    for ele in soup.select('div .table-td'):
        if len(ele.select('h4 a')) > 0 and len(ele.select('p.author a')) > 0:
            title = ele.select('h4 a')[0].get('title')
            author = ele.select('p.author a')[0].get('title')
            price = ele.select('ul.price.clearfix li b')[-1].text
            discount = ele.select('ul.price.clearfix li b')[0].text if len(ele.select('ul.price.clearfix li b')) == 2 else ''
            data.append([title, author, price, discount])

    return pd.DataFrame(data)

def download_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, header=False)
    output.seek(0)
    return output

# 加入自訂 CSS，調整表格欄位寬度
st.markdown("""
    <style>
        .table-container table {
            width: 100%;
            table-layout: auto;
        }
        .table-container td:nth-child(1) { width: 70%; } /* 書名 */
        .table-container td:nth-child(2) { width: 10%; } /* 作者 */
        .table-container td:nth-child(3) { width: 10%; } /* 價格 */
        .table-container td:nth-child(4) { width: 10%; } /* 折扣 */
    </style>
""", unsafe_allow_html=True)

# 建立標題
st.title("書籍搜尋系統")

# 使用 st.form 來支援按 Enter 送出搜尋
with st.form("search_form", clear_on_submit=True):
    search_str = st.text_input("輸入書名關鍵字", placeholder="例如：Python 入門")

    # 搜尋和提交按鈕，水平排列在搜尋框下方
    col1, col2 = st.columns([1, 1])
    with col1:
        search_button = st.form_submit_button("搜尋")

# 狀態變數，用於儲存搜尋結果
if "df" not in st.session_state:
    st.session_state.df = None

# 搜尋按鈕邏輯
if search_button and search_str:
    df = get_info(search_str)
    st.session_state.df = df  # 將搜尋結果儲存在 session state

    # 顯示搜尋結果的表格（隱藏索引和標題）
    html_table = df.to_html(index=False, header=False, classes="table table-striped")
    st.markdown(f'<div class="table-container">{html_table}</div>', unsafe_allow_html=True)

    # 如果有搜尋結果，顯示下載按鈕
    excel_data = download_excel(st.session_state.df)
    st.download_button(
        label="下載 Excel",
        data=excel_data,
        file_name="books_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif search_button:
    st.warning("請輸入書名關鍵字")
