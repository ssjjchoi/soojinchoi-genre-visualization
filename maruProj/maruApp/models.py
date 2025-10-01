from django.db import models


class Book(models.Model):
    location = models.CharField()           # 지점
    ranking = models.SmallIntegerField()    # 순위
    book_number = models.CharField()        # 고유ID
    title = models.CharField()              # 제목
    book_detail = models.CharField()        # 상세 페이지 링크
    book_img = models.CharField()           # 표지 이미지 링크
    author = models.CharField()             # 작가
    publisher = models.CharField()          # 출판사
    price = models.IntegerField()           # 가격
    score = models.FloatField()             # 리뷰 점수
    num_of_review = models.IntegerField()   # 리뷰 수
    genre = models.CharField()              # 장르