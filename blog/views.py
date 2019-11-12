from django.shortcuts import get_object_or_404, render
from .models import Blog, BlogType
from django.conf import settings
from django.db.models import Count
from django.core.paginator import Paginator
from read_statistics.utils import read_statistics_once_read
from django.contrib.contenttypes.models import ContentType

def blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每十篇进行分页
    page_num = request.GET.get('page', 1)  # 获取url的页面参数(GET)请求
    page_of_blogs = paginator.get_page(page_num)
    currenter_page_num = page_of_blogs.number  # 获取当前页码
    # 获取当前页码前后两页范围
    page_range = list(range(max(currenter_page_num - 2, 1), currenter_page_num)) + \
                 list(range(currenter_page_num, min(currenter_page_num + 2, paginator.num_pages) + 1))
    # 加上省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取博客分类对应的博客篇数
    '''blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''
    #或者使用：BlogType.objects.annotate(blog_count=Count('blog'))

    #获取日期归档的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog')) #有外键关联，给BlogType加注释拓展查询字段用annotate
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = blog_list_common_data(request, blogs_all_list)
    return render(request, 'blog/blog_list.html', context)

def blogs_with_type(request ,blog_type_id):
    blog_type = get_object_or_404(BlogType, id=blog_type_id)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = blog_list_common_data(request, blogs_all_list)
    context['blog_date'] = '%s年%s月' % (year, month)
    return render(request, 'blog/blogs_with_date.html', context)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    read_cookie_key = read_statistics_once_read(request, blog)
    blog_content_type = ContentType.objects.get_for_model(blog)
    #comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.id, parent=None)   #得到评论内容

    context = {}
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    #context['comments'] = comments.order_by('-comment_time')
    #context['comment_count'] = Comment.objects.filter(content_type=blog_content_type, object_id=blog.id).count()

    response = render(request, 'blog/blog_detail.html', context)#响应
    response.set_cookie(read_cookie_key, 'true')#阅读cookie标记
    return response