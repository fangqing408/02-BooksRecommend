from django.forms import model_to_dict
from .models import ad, BookReview


def Ad(request):
    # 查到广告页面佣金最多，也就是权重最大的返回到广告页面
    res = ad.objects.all().order_by('-order').first()
    # 拼接到 media 文件夹的本地文档里面防止丢失
    img = 'http://127.0.0.1:8000/media/' + str(res.img)
    return JsonResponse({'code':100, 'msg':'success', 'img':img})

def Books(request):
    # 获取所有书籍
    res = books.objects.all()
    ans = {}
    for x in res:
        # 在 cover_url 前面加上前缀，也是为了再 media 文件夹访问本地文档得到书籍的封面
        x.cover_url = 'http://127.0.0.1:8000/media/' + str(x.cover_url)
        # 将对象转换为字典，并添加到 ans 中
        book_dict = x.__dict__
        book_dict.pop('_state', None)
        # 移除 Django 模型内部的 _state 属性
        ans[x.id] = book_dict
    return JsonResponse({'code': 100, 'msg': 'success', 'data': ans})

def User(request):
    username = request.GET.get('username')
    res = users.objects.filter(username=username).first()
    user = users.objects.get(username=username)
    liked_books = user.liked_books.values_list('id', flat=True)
    res_dict = model_to_dict(res)  # 将模型实例转换为字典
    res_dict['avatar'] = 'http://127.0.0.1:8000/media/' + str(res.avatar)  # 修改 avatar 字段
    res_dict['liked_books'] = list(liked_books)
    return JsonResponse({'code': 100, 'msg': 'success', 'data': res_dict})

import json
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def record_reading(request):
    # 前端传输信息到后端的请求 POST
    if request.method == 'POST':
        try:
            # 得到书籍id，用户名，阅读时长
            data = json.loads(request.body)
            book_id = data.get('bookId')
            username = data.get('username')
            duration = int(data.get('duration'))
            # 获取书籍对象
            book = books.objects.get(id=book_id)
            # 获取用户对象
            user = users.objects.get(username=username)
            # 更新书籍的点击量和阅读时长
            book.click_count += 1
            book.read_duration += duration // 1000  # 将毫秒转换为秒
            # 更新用户的阅读时长和总时长
            book.save()
            category = book.category
            if category == '神话':
                user.myth_duration += duration // 1000
            elif category == '仙侠':
                user.xianxia_duration += duration // 1000
            elif category == '武侠':
                user.wuxia_duration += duration // 1000
            elif category == '科幻':
                user.scifi_duration += duration // 1000
            elif category == '悬疑':
                user.mystery_duration += duration // 1000
            elif category == '古代':
                user.historical_duration += duration // 1000
            elif category == '现代':
                user.modern_duration += duration // 1000
            user.total_duration += duration // 1000
            user.save()
            return JsonResponse({'status': 'success', 'message': '数据记录成功'})
        except books.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '书籍不存在'}, status=404)
        except users.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except (KeyError, ValueError, TypeError) as e:
            return JsonResponse({'status': 'error', 'message': f'参数错误: {str(e)}'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

from django.http import JsonResponse
from .models import books, users

from django.http import JsonResponse
from .models import books, users

from django.http import JsonResponse
from .models import books, users

from django.http import JsonResponse
from .models import users, books

def recommend(request):
    # 得到小程序端传的参数 username 是唯一的
    username = request.GET.get('username')
    try:
        # 获取用户对象
        user = users.objects.get(username=username)
        # 找到用户每类图书观看总时长最大的类别
        category_durations = {
            '神话': user.myth_duration,
            '仙侠': user.xianxia_duration,
            '武侠': user.wuxia_duration,
            '科幻': user.scifi_duration,
            '悬疑': user.mystery_duration,
            '古代': user.historical_duration,
            '现代': user.modern_duration,
        }
        max_category = max(category_durations, key=category_durations.get)
        # 获取该类别下的所有书籍
        books_in_category = books.objects.filter(category=max_category)
        # 计算每本书的综合评分
        weighted_books = []
        for book in books_in_category:
            # 综合评分 = (阅读时长 * 0.6) + (点击量 * 0.4)
            weighted_score = (book.read_duration * 0.6) + (book.click_count * 0.4)
            weighted_books.append({
                'book': book,
                'weighted_score': weighted_score,
            })
        # 根据综合评分排序，推荐前两本书
        sorted_books = sorted(weighted_books, key=lambda x: x['weighted_score'], reverse=True)
        first_two_books = [item['book'] for item in sorted_books[:2]]
        # 根据用户年龄推荐第三本书
        category_order = ['神话', '仙侠', '武侠', '科幻', '悬疑', '古代', '现代']
        age_thresholds = [18, 25, 35, 45, 55, 65]  # 年龄分段
        if user.age < age_thresholds[0]:
            third_category = category_order[0]  # 神话
        elif user.age < age_thresholds[1]:
            third_category = category_order[1]  # 仙侠
        elif user.age < age_thresholds[2]:
            third_category = category_order[2]  # 武侠
        elif user.age < age_thresholds[3]:
            third_category = category_order[3]  # 科幻
        elif user.age < age_thresholds[4]:
            third_category = category_order[4]  # 悬疑
        elif user.age < age_thresholds[5]:
            third_category = category_order[5]  # 古代
        else:
            third_category = category_order[6]  # 现代
        # 获取第三本书
        third_book = books.objects.filter(category=third_category).order_by('-click_count').first()
        # 推荐第四本：热门书籍（点击量最高的书籍）
        popular_book = books.objects.order_by('-click_count').first()
        # 推荐第五本：新书（最近添加的书籍）
        new_book = books.objects.order_by('-added_time').first()
        # 将推荐的书整理成结果，并去重
        recommended_books = []
        # 用于记录已经添加的书籍 ID
        seen_books = set()
        # 添加前两本书
        for book in first_two_books:
            if book.id not in seen_books:
                book_dict = {
                    'id': book.id,
                    'title': book.name,
                    'cover_url': 'http://127.0.0.1:8000/media/' + str(book.cover_url),
                    'category': book.category,
                    'click_count': book.click_count,
                    'read_duration': book.read_duration,
                    'description': book.description,
                }
                recommended_books.append(book_dict)
                seen_books.add(book.id)
        # 添加第三本书
        if third_book and third_book.id not in seen_books:
            third_book_dict = {
                'id': third_book.id,
                'title': third_book.name,
                'cover_url': 'http://127.0.0.1:8000/media/' + str(third_book.cover_url),
                'category': third_book.category,
                'click_count': third_book.click_count,
                'read_duration': third_book.read_duration,
                'description': third_book.description
            }
            recommended_books.append(third_book_dict)
            seen_books.add(third_book.id)
        # 添加第四本书（热门书籍）
        if popular_book and popular_book.id not in seen_books:
            popular_book_dict = {
                'id': popular_book.id,
                'title': popular_book.name,
                'cover_url': 'http://127.0.0.1:8000/media/' + str(popular_book.cover_url),
                'category': popular_book.category,
                'click_count': popular_book.click_count,
                'read_duration': popular_book.read_duration,
                'description': popular_book.description
            }
            recommended_books.append(popular_book_dict)
            seen_books.add(popular_book.id)
        # 添加第五本书（新书）
        if new_book and new_book.id not in seen_books:
            new_book_dict = {
                'id': new_book.id,
                'title': new_book.name,
                'cover_url': 'http://127.0.0.1:8000/media/' + str(new_book.cover_url),
                'category': new_book.category,
                'click_count': new_book.click_count,
                'read_duration': new_book.read_duration,
                'description': new_book.description
            }
            recommended_books.append(new_book_dict)
            seen_books.add(new_book.id)
        return JsonResponse({'status': 'success', 'data': recommended_books})
    except users.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import users

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            # 获取用户对象
            user = users.objects.get(username=username)
            # 验证密码
            if user.check_password(password):
                return JsonResponse({'status': 'success', 'message': '登录成功', 'user_id': user.user_id})
            else:
                return JsonResponse({'status': 'error', 'message': '密码错误'}, status=400)
        except users.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
        except (KeyError, ValueError, TypeError) as e:
            return JsonResponse({'status': 'error', 'message': f'参数错误: {str(e)}'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': '请求方法不支持'}, status=405)

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import users

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        age = int(data.get('age'))
        gender = data.get('gender')
        print(username, password, age, gender)
        # 检查用户名是否已存在
        if users.objects.filter(username=username).exists():
            return JsonResponse({'code': 400, 'msg': '用户名已存在', 'data': None})

        # 创建新用户
        try:
            new_user = users.objects.create(
                username=username,
                password=password,  # 实际项目中需要对密码进行加密
                age=age,
                gender=gender,
            )
            return JsonResponse({'code': 100, 'msg': '注册成功', 'data': {'user_id': new_user.user_id}})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e), 'data': None})
    else:
        return JsonResponse({'code': 405, 'msg': '方法不允许', 'data': None})

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import books

@csrf_exempt
def update_rating(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        book_id = data.get('book_id')  # 获取书的 id
        rating = float(data.get('rating'))  # 获取评分

        try:
            book = books.objects.get(id=book_id)  # 根据 id 查找书籍
            book.rate += rating  # 更新总评分
            book.people_count += 1  # 更新评分人数
            book.save()

            return JsonResponse({'code': 100, 'msg': '评分成功', 'data': None})
        except books.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '书籍不存在', 'data': None})
    else:
        return JsonResponse({'code': 405, 'msg': '方法不允许', 'data': None})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import users

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Discussion

@csrf_exempt
def get_discussions(request):
    if request.method == 'GET':
        discussions = Discussion.objects.filter(is_deleted=False).order_by('-created_at')
        discussion_list = [
            {
                'id': discussion.id,
                'content': discussion.content,
                'username': discussion.username,
                'created_at': discussion.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for discussion in discussions
        ]
        return JsonResponse({'code': 100, 'msg': 'success', 'data': discussion_list})
    else:
        return JsonResponse({'code': 405, 'msg': '方法不允许', 'data': None})
@csrf_exempt
def delete_discussion(request):
    data = json.loads(request.body)
    if request.method == 'POST':

        comment_id = data.get('id')
        username = data.get('username')
        print(f"Attempting to delete comment {comment_id} for user {username}")  # 添加这行

        try:
            comment = Discussion.objects.get(id=comment_id, username=username)
            comment.is_deleted = True  # 软删除
            comment.save()
            return JsonResponse({'code': 100, 'msg': '删除成功'})
        except Discussion.DoesNotExist:
            return JsonResponse({'code': 101, 'msg': '评论不存在或无权删除'})
@csrf_exempt
def update_duration(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        username = data.get('username')  # 假设通过 user_id 更新用户数据
        categories = data.get('categories')  # 获取需要更新的分类
        print(categories)
        try:
            user = users.objects.get(username=username)
            for category in categories:
                duration_field = f'{category}_duration'
                if getattr(user, duration_field) < 500:
                    setattr(user, duration_field, getattr(user, duration_field) + 500)
            user.save()

            return JsonResponse({'code': 100, 'msg': '更新成功', 'data': None})
        except users.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '用户不存在', 'data': None})
    else:
        return JsonResponse({'code': 405, 'msg': '方法不允许', 'data': None})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Discussion

@csrf_exempt
def add_discussion(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        content = data.get('content')
        username = data.get('username')

        if not content or not username:
            return JsonResponse({'code': 400, 'msg': '内容或用户名不能为空', 'data': None})

        # 创建新的讨论内容
        discussion = Discussion.objects.create(
            content=content,
            username=username,
        )
        return JsonResponse({'code': 100, 'msg': '发送成功', 'data': None})
    else:
        return JsonResponse({'code': 405, 'msg': '方法不允许', 'data': None})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import users, books

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import users, books

@csrf_exempt
def like_book(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        username = data.get('username')
        book_id = data.get('book_id')
        try:
            user = users.objects.get(username=username)
            book = books.objects.get(id=book_id)
            user.liked_books.add(book)
            return JsonResponse({'code': 100, 'msg': '收藏成功'})
        except users.DoesNotExist:
            return JsonResponse({'code': 103, 'msg': '用户不存在'})
        except books.DoesNotExist:
            return JsonResponse({'code': 104, 'msg': '书籍不存在'})
    return JsonResponse({'code': 101, 'msg': '请求方法错误'})

@csrf_exempt
def unlike_book(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        username = data.get('username')
        book_id =data.get('book_id')
        try:
            user = users.objects.get(username=username)
            book = books.objects.get(id=book_id)
            user.liked_books.remove(book)
            return JsonResponse({'code': 100, 'msg': '取消收藏成功'})
        except users.DoesNotExist:
            return JsonResponse({'code': 103, 'msg': '用户不存在'})
        except books.DoesNotExist:
            return JsonResponse({'code': 104, 'msg': '书籍不存在'})
    return JsonResponse({'code': 101, 'msg': '请求方法错误'})

@csrf_exempt
def get_liked_books(request):
    username = request.GET.get('username')
    if request.method == 'GET':
        user = users.objects.get(username=username)
        liked_books = user.liked_books.values_list('id', flat=True)
        return JsonResponse({'code': 100, 'data': list(liked_books)})
    return JsonResponse({'code': 101, 'msg': '请求方法错误'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_book_reviews(request):
    """获取指定书籍的所有书评"""
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        reviews = BookReview.objects.filter(
            book_id=book_id,
            is_deleted=False
        ).order_by('-created_at')

        review_list = [{
            'id': r.id,
            'content': r.content,
            'username': r.username,
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for r in reviews]

        return JsonResponse({'code': 100, 'data': review_list})
    return JsonResponse({'code': 405, 'msg': 'Method not allowed'}, status=405)

@csrf_exempt
def create_review(request):
    """创建新书评"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            BookReview.objects.create(
                book_id=data['book_id'],
                content=data['content'],
                username=data['username']
            )
            return JsonResponse({'code': 100, 'msg': '书评发表成功'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)}, status=500)
    return JsonResponse({'code': 405, 'msg': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_book_review(request):
    """删除书评"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            review = BookReview.objects.get(
                id=data['id'],
                username=data['username'],  # 确保只能删除自己的书评
                is_deleted=False
            )
            review.is_deleted = True
            review.save()
            return JsonResponse({'code': 100, 'msg': '删除成功'})

        except BookReview.DoesNotExist:
            return JsonResponse({'code': 404, 'msg': '书评不存在或无权删除'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': str(e)})
    return JsonResponse({'code': 405, 'msg': '方法不允许'})

def get_book_details(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')
        res = books.objects.filter(id=book_id)
        ans = {}
        for x in res:
            # 在 cover_url 前面加上前缀，也是为了再 media 文件夹访问本地文档得到书籍的封面
            x.cover_url = 'http://127.0.0.1:8000/media/' + str(x.cover_url)
            # 将对象转换为字典，并添加到 ans 中
            book_dict = x.__dict__
            book_dict.pop('_state', None)
            # 移除 Django 模型内部的 _state 属性
            ans[x.id] = book_dict
        return JsonResponse({'code': 100, 'msg': 'success', 'data': ans})