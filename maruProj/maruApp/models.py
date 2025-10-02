from django.db import models


class Book(models.Model):
    location = models.CharField(max_length=50)          # 지점
    ranking = models.SmallIntegerField()                # 순위
    book_number = models.CharField(max_length=50)       # 고유ID
    title = models.CharField(max_length=50)             # 제목
    book_detail = models.CharField(max_length=100)      # 상세 페이지 링크
    book_img = models.CharField(max_length=100)         # 표지 이미지 링크
    author = models.CharField(max_length=50)            # 작가
    publisher = models.CharField(max_length=50)         # 출판사
    price = models.IntegerField()                       # 가격
    score = models.FloatField()                         # 리뷰 점수
    num_of_review = models.IntegerField()               # 리뷰 수
    genre = models.CharField(max_length=50)             # 장르
