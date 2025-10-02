import io
import json
import pandas as pd
from typing import Counter
from django.http import HttpResponse
from django.shortcuts import render
from .models import Book
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rc
from io import BytesIO
import base64
from django.views.decorators.cache import never_cache


# Mac 한글 폰트 설정
rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# json 경로
# JSON_PATH = 'maruApp/data/test.json'    # 연습용
JSON_PATH = 'maruApp/data/bestseller_all.json'


# json 파일을 읽어서 Book 객체 리스트로 반환하는 함수
def load_books_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    books = []
    for item in data:
        book = Book(
            location=item.get('location', ''),
            ranking=item.get('ranking', 0),
            book_number=item.get('book_number', ''),
            title=item.get('title', ''),
            book_detail=item.get('book_detail', ''),
            book_img=item.get('book_img', ''),
            author=item.get('author', ''),
            publisher=item.get('publisher', ''),
            price=item.get('price', 0),
            score=item.get('score', 0),
            num_of_review=item.get('num_of_review', 0),
            genre=item.get('genre', ''),
        )
        books.append(book)
    return books


# 장르 분포 (원형 차트)
@never_cache
def genre_chart(request):
    books = load_books_from_json(JSON_PATH)
    
    # 카테고리별 개수 집계
    genres = [book.genre for book in books]
    counter = Counter(genres)
    labels = list(counter.keys())
    sizes = list(counter.values())

    plt.figure(figsize=(5, 4))  # 더 넓게
    # 각 카테고리별 % 계산
    total = sum(sizes)
    percent_data = sorted(
        zip(labels, sizes, [size/total*100 for size in sizes]),
        key=lambda x: x[2], reverse=True
    )
    sorted_labels = [label for label, _, _ in percent_data]
    sorted_sizes = [size for _, size, _ in percent_data]
    sorted_percent_labels = [f"{label} ({percent:.1f}%)" for label, _, percent in percent_data]

    fig = plt.figure(figsize=(7, 5.5))  # 높이 더 줄임
    patches, texts = plt.pie(
        sorted_sizes,
        labels=None,
        autopct=None,
        startangle=140,
        pctdistance=0.8,
        labeldistance=1.1
    )
    plt.legend(patches, sorted_percent_labels, loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=12)
    plt.subplots_adjust(top=0.97, bottom=0.07)  # 여백 더 줄임
    plt.axis('equal')
    plt.tight_layout(pad=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05)
    plt.close('all')
    buf.seek(0)
    
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


# 지역별 평균 가격 (막대 차트)
@never_cache
def price_by_location_chart(request):
    books = load_books_from_json(JSON_PATH)

    # Book 객체 → DataFrame 변환
    df = pd.DataFrame([{
        "location": b.location,
        "price": float(str(b.price).replace(",", ""))  # price 정수/문자 혼용 처리
    } for b in books])

    # 지역별 평균 가격
    avg_price = df.groupby("location")["price"].mean().sort_values()

    # 시각화
    plt.figure(figsize=(7,4))
    avg_price.plot(kind="bar", color="skyblue", edgecolor="black")
    # plt.title("지역별 평균 가격 비교", fontsize=14)
    plt.ylabel("평균 가격(원)", fontsize=12)
    plt.xlabel("지역", fontsize=12)
    plt.xticks(rotation=45)

    # PNG 이미지로 반환
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")   # format="jpg" 도 가능
    plt.close('all')
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response