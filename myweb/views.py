from django.shortcuts import render  #redirect为跳转方法
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog
from django.db.models import Sum
from django.utils import timezone
import datetime
from django.core.cache import cache


def get_7days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lte=today, read_details__date__gte=date).values('id', 'title')\
                .annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')#用values与annotate实现分组统计
    return blogs[:5]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)
    #获取7天热门博客的缓存数据
    hot_blogs_for_7days = cache.get('hot_blogs_for_7days')
    if hot_blogs_for_7days is None:
        hot_blogs_for_7days = get_7days_hot_blogs()
        cache.set('hot_blogs_for_7days', hot_blogs_for_7days, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['hot_blogs_for_7days'] = hot_blogs_for_7days
    return render(request, 'home.html', context)

