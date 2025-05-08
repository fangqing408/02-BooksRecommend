from django.db import models
# Create your models here.
class ad(models.Model):
    img = models.ImageField(upload_to='ad', default='/ad/default.png')
    order = models.IntegerField(default=0)
    creat_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    class Meta:
        verbose_name = "广告"
        verbose_name_plural = "广告"

class books(models.Model):
    name = models.CharField(max_length=200, verbose_name="书名")
    author = models.CharField(max_length=100, verbose_name="作者")
    category = models.CharField(max_length=50, verbose_name="类型")
    added_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否被删除")
    click_count = models.PositiveIntegerField(default=0, verbose_name="点击量")
    read_duration = models.PositiveIntegerField(default=0, verbose_name="阅读时长")
    description = models.TextField(blank=True, null=True, verbose_name="简介")
    cover_url = models.ImageField(blank=True, null=True, verbose_name="封面链接", upload_to='books', default='/books/default.png')
    rate = models.FloatField(default=5.0, verbose_name="评分")
    people_count = models.PositiveIntegerField(default=1, verbose_name="评分人数")
    liked_by = models.ManyToManyField('users', related_name='liked_books_by_user', blank=True, verbose_name="喜欢这本书的用户")

    class Meta:
        verbose_name = "书库"
        verbose_name_plural = "书库"
    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class users(models.Model):
    user_id = models.AutoField(primary_key=True, verbose_name="用户号")
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名字")
    age = models.PositiveIntegerField(verbose_name="年纪")
    points = models.PositiveIntegerField(default=0, verbose_name="积分")
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], verbose_name="性别")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="用户头像", default='/avatars/default.png')
    password = models.CharField(default='123456', max_length=128, verbose_name="用户密码")  # 存储加密后的密码
    myth_duration = models.PositiveIntegerField(default=0, verbose_name="神话观看总时长")
    xianxia_duration = models.PositiveIntegerField(default=0, verbose_name="仙侠观看总时长")
    wuxia_duration = models.PositiveIntegerField(default=0, verbose_name="武侠观看总时长")
    scifi_duration = models.PositiveIntegerField(default=0, verbose_name="科幻观看总时长")
    mystery_duration = models.PositiveIntegerField(default=0, verbose_name="悬疑观看总时长")
    historical_duration = models.PositiveIntegerField(default=0, verbose_name="古代观看总时长")
    modern_duration = models.PositiveIntegerField(default=0, verbose_name="现代观看总时长")
    total_duration = models.PositiveIntegerField(default=0, verbose_name="观看所有图书的总时长")
    liked_books = models.ManyToManyField('books', related_name='liked_users_by_book', blank=True, verbose_name="用户喜欢的书")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username
    def check_password(self, raw_password):
        """验证密码"""
        return raw_password == self.password

from django.db import models

class Discussion(models.Model):
    content = models.TextField(verbose_name="内容")
    username = models.CharField(max_length=100, verbose_name="用户名")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否被删除")

    class Meta:
        verbose_name = "讨论区"
        verbose_name_plural = "讨论区"

    def __str__(self):
        return f"{self.username}: {self.content[:20]}..."

from django.db import models

class BookReview(models.Model):
    """书评模型（简化版）"""
    book = models.ForeignKey(
        'books',
        on_delete=models.CASCADE,  # 书籍删除时级联删除书评
        verbose_name="关联图书",
        related_name='reviews'  # 通过book.reviews访问所有书评
    )
    content = models.TextField(verbose_name="评价内容")
    username = models.CharField(max_length=100, verbose_name="用户名")  # 直接存用户名，简化关联
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发表时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        ordering = ['-created_at']  # 默认按时间倒序
        verbose_name = "书评"
        verbose_name_plural = "书评"

    def __str__(self):
        return f"{self.username}对《{self.book.name}》的评论"