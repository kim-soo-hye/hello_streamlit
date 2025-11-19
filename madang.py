import streamlit as st
import duckdb
import pandas as pd
import time

# DuckDB 연결
conn = duckdb.connect('madang.db')

def query(sql):
    return conn.sql(sql).df()

# 책 목록 로드
books = [None]
result = query("SELECT bookid || ',' || bookname AS item FROM Book")
for row in result['item']:
    books.append(row)

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

name = ""
custid = 999
result_df = pd.DataFrame()
name = tab1.text_input("고객명")
select_book = ""

# -------------------
#  고객 조회 탭
# -------------------
if len(name) > 0:
    sql = f"""
        SELECT 
            c.custid, 
            c.name, 
            b.bookname, 
            o.orderdate, 
            o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON o.bookid = b.bookid
        WHERE c.name = '{name}'
    """
    result_df = query(sql)
    tab1.write(result_df)

    # 고객 정보 표시
    custid = int(result_df['custid'][0])
    tab2.write("고객번호: " + str(custid))
    tab2.write("고객명: " + name)

    # ---------------------------------
    # 구매 Input UI
    # ---------------------------------
    select_book = tab2.selectbox("구매 서적:", books)

    if select_book is not None:
        bookid = select_book.split(",")[0]

        # 오늘 날짜
        dt = time.strftime('%Y-%m-%d', time.localtime())

        # 새로운 orderid 생성
        max_order = query("SELECT COALESCE(MAX(orderid),0) AS max_id FROM Orders") 
        orderid = int(max_order['max_id'][0]) + 1

        # 가격 입력
        price = tab2.text_input("금액")

        # 버튼 클릭 → 주문 insert
        if tab2.button("거래 입력"):
            insert_sql = f"""
                INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                VALUES ({orderid}, {custid}, {bookid}, {price}, '{dt}')
            """
            conn.sql(insert_sql)
            tab2.success("거래가 입력되었습니다!")
