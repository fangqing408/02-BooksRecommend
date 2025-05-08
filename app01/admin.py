from django.contrib import admin

# Register your models here.
from .models import ad, books, users, Discussion, BookReview
admin.site.register(Discussion)
@admin.register(users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'age', 'gender')  # 列表页显示的字段
    filter_horizontal = ('liked_books',)  # 使用水平过滤器，方便选择喜欢的书
    # 其他配置...

@admin.register(books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'category')  # 列表页显示的字段
    filter_horizontal = ('liked_by',)  # 使用水平过滤器，方便选择喜欢的用户

admin.site.register(BookReview)