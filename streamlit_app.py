import streamlit_app as st
from app import app  # 假設您的 Flask 應用在 app.py 中


def run():
    st.write("Flask app is running...")
    # 這裡可以添加一個鏈接到您的 Flask 應用
    st.markdown("[Open Flask App](http://localhost:7860)")


if __name__ == "__main__":
    run()
