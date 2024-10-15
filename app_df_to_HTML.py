import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, send_file, session
import io
import os


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

    # getH4 = getEle.find('h4')
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

        ele_arr.append(arr)
    return pd.DataFrame(ele_arr)

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        df = Get_Info(request.form.get('searchStr'))
        html_table = df.to_html(
            classes='table table-striped', index=False, header=False)
        tempArr = df.values.tolist()
        session['tempArr'] = tempArr  # 将 tempArr 保存到 session 中
        return render_template('index_table.html',  data=html_table)
    else:
        html_table = '''
        <table class="table table-striped">
            <tbody>
                <tr>
                    <td>請輸入要查詢的名稱</td>
                </tr>
            </tbody>
        </table>
        '''
        return render_template('index_table.html', data=html_table)


@app.route('/download')
def download_excel():
    # 获取数据并存储到Excel文件中
    # 从 session 中获取 tempArr
    tempArr = session.get('tempArr')

    if tempArr:
        # 将 tempArr 转换为 pandas DataFrame
        df = pd.DataFrame(tempArr)
    else:
        df = pd.DataFrame([['No data']])

    # 使用 io.BytesIO 将 Excel 文件保存在内存中
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
    output.seek(0)

    # 将 Excel 文件作为附件发送给用户
    return send_file(output,
                     download_name="data.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                     )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # 預設埠為 5000
    app.run(host='0.0.0.0', port=port, debug=True)
