import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, send_file, session
import io

# 爬取網站函數


def Get_Info(searchStr):

    searchBox = searchStr

    url = 'https://search.books.com.tw/search/query/key/' + \
        searchBox + '/cat/all/fclick/autocmp-pc'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    }

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'lxml')

    getEle = soup.select('div .table-td')

    ele_arr = [['書名', '作者', '價格', '折扣']]
    for ele in getEle:
        if len(ele.select('h4 a')) > 0 and len(ele.select('p.author a')) > 0:
            getTitle = ele.select('h4 a')[0].get('title')
            author = ele.select('p.author a')[0].get('title')
            getPrice = ele.select('ul.price.clearfix li b')
            price = ''
            promotion = ''
            if len(ele.select('ul.price.clearfix li b')) == 2:
                price = ele.select('ul.price.clearfix li b')[1].contents
                promotion = ele.select('ul.price.clearfix li b')[0].contents
            else:
                price = ele.select('ul.price.clearfix li b')[0].contents
            arr = [getTitle, author, price, promotion]
            # print(f'書名:{getTitle}, 作者:{author}, 價格:{price}, 折扣:{promotion}')

        ele_arr.append(arr)

    return ele_arr


app = Flask(__name__)

app.secret_key = 'test_secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tempArr = Get_Info(request.form.get('searchStr'))
        # 將 tempArr 保存到 session 中 給download_excel使用
        session['tempArr'] = tempArr
        return render_template('index.html', data=tempArr)
    else:
        return render_template('index.html', data=[['請輸入要查詢的名稱']])


@app.route('/download')
def download_excel():

    tempArr = session.get('tempArr')
    if tempArr:
        # 轉轉換dataframe
        df = pd.DataFrame(tempArr)
    else:
        df = pd.DataFrame([['No data']])

    # 使用 io.BytesIO 将 Excel 文件存在記憶體
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
    output.seek(0)

    # 下載檔案
    return send_file(output,
                     download_name="data.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                     )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
