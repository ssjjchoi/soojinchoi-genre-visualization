import io
import json
from typing import Counter
from django.http import HttpResponse
from django.shortcuts import render
from .models import Book
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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



def book_chart(request):
    books = load_books_from_json('maruApp/data/test.json')                     # 연습용 데이터
    
    # 카테고리별 개수 집계
    genres = [book.genre for book in books]
    counter = Counter(genres)
    labels = list(counter.keys())
    sizes = list(counter.values())

    # 한글 폰트 설정 (Apple 기본 폰트 사용)
    matplotlib.rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False

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
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05)  # pad_inches로 여백 최소화
    plt.close()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')