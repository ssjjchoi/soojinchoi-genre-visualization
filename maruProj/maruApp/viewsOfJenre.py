import io 
import json
import os
import re
from collections import Counter
import random

import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
from django.http import JsonResponse, HttpResponse 
from django.shortcuts import render
from django.db.models import F, FloatField, Sum

from .models import Book


matplotlib.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False


# JSON_PATH = 'maruApp/data/bestseller_all.json'
JSON_PATH = os.path.join(settings.BASE_DIR, 'maruApp', 'data', 'bestseller_all.json')


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

# ----------------------------

def genre_page(request):
    """장르 페이지 HTML 렌더"""
    top_books_list = genre_top3()
    return render(request, 'maru/genre.html', {'top_books_list': top_books_list})


# Chart.js

def genre_data(request):
    """장르별 권수 + 퍼센트 JSON 반환"""
    books = load_books_from_json(JSON_PATH)
    genres = [book.genre for book in books]
    counter = Counter(genres)
    total = sum(counter.values())
    
    # 권수와 퍼센트 계산
    data = []
    for g, c in counter.items():
        percent = round(c / total * 100, 1)
        data.append({'genre': g, 'count': c, 'percent': percent})
    
    return JsonResponse(data, safe=False)


# -----------------------------
# 이전 버전: 장르별 GMV만 계산 (툴팁 내부 평균 리뷰/가격/점수 미포함)
# 참고용으로 남겨둠, 현재는 아래 함수 사용
# -----------------------------
# def genre_gmv_data(request):
#     books = load_books_from_json(JSON_PATH)

#     gmv_by_genre = {}
#     for book in books:
#         try:
#             # 가격 문자열에서 숫자만 추출 (예: "12,000원" → "12000")
#             price_str = str(book.price)
#             price_clean = re.sub(r'[^0-9.]', '', price_str)  
#             price = float(price_clean) if price_clean else 0

#             # 리뷰 수
#             reviews_str = str(book.num_of_review)
#             reviews_clean = re.sub(r'[^0-9]', '', reviews_str)
#             reviews = int(reviews_clean) if reviews_clean else 0

#             # 평점
#             score_str = str(book.score)
#             score_clean = re.sub(r'[^0-9.]', '', score_str)
#             score = float(score_clean) if score_clean else 0

#         except ValueError:
#             price, reviews, score = 0, 0, 0

#         gmv = price * reviews * score
#         gmv_by_genre[book.genre] = gmv_by_genre.get(book.genre, 0) + gmv

#     data = [{"genre": g, "gmv": round(v, 2)} for g, v in gmv_by_genre.items()]
#     return JsonResponse(data, safe=False)


def genre_gmv_data(request):
    books = load_books_from_json(JSON_PATH)

    genre_stats = {}

    for book in books:
        try:
            price_str = str(book.price)
            price_clean = re.sub(r'[^0-9.]', '', price_str)
            price = float(price_clean) if price_clean else 0

            reviews_str = str(book.num_of_review)
            reviews_clean = re.sub(r'[^0-9]', '', reviews_str)
            reviews = int(reviews_clean) if reviews_clean else 0

            score_str = str(book.score)
            score_clean = re.sub(r'[^0-9.]', '', score_str)
            score = float(score_clean) if score_clean else 0
        except ValueError:
            price, reviews, score = 0, 0, 0

        gmv = price * reviews * score

        if book.genre not in genre_stats:
            genre_stats[book.genre] = {
                "gmv": 0,
                "price_sum": 0,
                "review_sum": 0,
                "score_sum": 0,
                "count": 0
            }

        genre_stats[book.genre]["gmv"] += gmv
        genre_stats[book.genre]["price_sum"] += price
        genre_stats[book.genre]["review_sum"] += reviews
        genre_stats[book.genre]["score_sum"] += score
        genre_stats[book.genre]["count"] += 1

    # 평균 구하기
    data = []
    for genre, stats in genre_stats.items():
        count = stats["count"]
        avg_price = stats["price_sum"] / count if count else 0
        avg_reviews = stats["review_sum"] / count if count else 0
        avg_score = stats["score_sum"] / count if count else 0

        data.append({
            "genre": genre,
            "gmv": round(stats["gmv"], 2),
            "price": round(avg_price, 2),
            "num_of_review": int(avg_reviews),
            "score": round(avg_score, 2)
        })

    return JsonResponse(data, safe=False)


def genre_top3_json(request):
    books = load_books_from_json(JSON_PATH)
    data = []

    for b in books:
        if not b.book_img:
            continue
        data.append({
            'book_number': getattr(b, 'book_number', None),
            'title': b.title,
            'author': b.author,
            'genre': b.genre,
            'price': b.price,
            'num_of_review': b.num_of_review,
            'score': b.score,
            'book_img': b.book_img,
            'book_detail': b.book_detail
        })

    df = pd.DataFrame(data)

    # 숫자 변환
    df['price'] = df['price'].apply(lambda x: float(re.sub(r'[^0-9.]','', str(x))) if x else 0)
    df['num_of_review'] = df['num_of_review'].apply(lambda x: int(re.sub(r'[^0-9]','', str(x))) if x else 0)
    df['score'] = df['score'].apply(lambda x: float(re.sub(r'[^0-9.]','', str(x))) if x else 0)

    # GMV 계산
    df['gmv'] = df['price'] * df['num_of_review'] * df['score']

    # 중복 제거: book_number 기준
    if 'book_number' in df.columns:
        df = df.sort_values('gmv', ascending=False).drop_duplicates('book_number')
    else:
        df = df.sort_values('gmv', ascending=False).drop_duplicates(['title','author'])

    # 장르별 top3
    result = {}
    for genre, g in df.groupby('genre'):
        top3 = g.sort_values('gmv', ascending=False).head(3)
        result[genre] = top3[['title','book_img','gmv','book_detail']].to_dict(orient='records')

        # book_detail 누락 안전망
        columns = ['title','book_img','gmv']
        if 'book_detail' in df.columns:
            columns.append('book_detail')

    return JsonResponse(result)


def genre_price_data(request):
    """장르별 가격 통계 JSON 반환"""
    books = load_books_from_json(JSON_PATH)
    data = []

    for b in books:
        if not b.price:
            continue
        data.append({
            'genre': b.genre,
            'price': float(re.sub(r'[^0-9.]','', str(b.price))) if b.price else 0
        })

    df = pd.DataFrame(data)
    # 장르별 평균/최고/최저 가격
    price_stats = df.groupby('genre')['price'].agg(['mean','max','min']).reset_index()
    price_stats = price_stats.round(2)
    
    # JSON 변환
    result = price_stats.to_dict(orient='records')
    return JsonResponse(result, safe=False)


def genre_recommend_top3(request):
    books = load_books_from_json(JSON_PATH)
    data = []

    for b in books:
        if not b.book_img:
            continue
        try:
            score = float(re.sub(r'[^0-9.]','', str(b.score))) if b.score else 0
            reviews = int(re.sub(r'[^0-9]','', str(b.num_of_review))) if b.num_of_review else 0
        except:
            score, reviews = 0, 0

        data.append({
            'title': b.title,
            'book_img': b.book_img,
            'book_detail': b.book_detail,
            'score': score,
            'num_of_review': reviews,
            'ranking': b.ranking
        })

    df = pd.DataFrame(data)

    # 추천 점수 계산 (가격 제외)
    # df['recommend_score'] = df['score'] * 2 + df['num_of_review'] * 0.1 + (100 - df['ranking'])*0.05
    # df['recommend_score'] = df['score'] * 0.5 + df['num_of_review'] * 0.1 + (100 - df['ranking'])*2
    df['recommend_score'] = df['score'] * 0.5 + df['num_of_review'] * 2 + (100 - df['ranking'])*0.1


    # 상위 25권 추출 후, title 기준 중복 제거
    top25 = df.sort_values('recommend_score', ascending=False).head(25)
    top25 = top25.drop_duplicates(subset='title')  # 중복된 책 제거

    # 랜덤 3권 추천
    recommended = top25.sample(3).to_dict(orient='records')

    return JsonResponse(recommended, safe=False)


def genre_heatmap(request):
    """장르별 price/score/reviews/gmv 히트맵용 JSON 반환"""
    books = load_books_from_json(JSON_PATH)
    data = []

    for b in books:
        try:
            price = float(re.sub(r'[^0-9.]','', str(b.price))) if b.price else 0
            score = float(re.sub(r'[^0-9.]','', str(b.score))) if b.score else 0
            reviews = int(re.sub(r'[^0-9]','', str(b.num_of_review))) if b.num_of_review else 0
            gmv = price * score * reviews
        except:
            price, score, reviews, gmv = 0, 0, 0, 0

        data.append({
            'genre': b.genre,
            'price': price,
            'score': score,
            'num_of_review': reviews,
            'gmv': gmv
        })

    df = pd.DataFrame(data)
    # 장르별 평균
    genre_avg = df.groupby('genre')[['price','score','num_of_review','gmv']].mean().round(2)
    result = genre_avg.to_dict(orient='index')  # { '소설': {'price': ..., 'score': ..., 'num_of_review': ..., 'gmv': ...}, ... }

    return JsonResponse(result)

