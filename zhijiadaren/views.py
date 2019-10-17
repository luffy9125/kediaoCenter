from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read

# Create your views here.


# 公共代码
def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每2篇进行分页
    page_num = request.GET.get('page', 1)   # 获取页面参数(GET请求)
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number # 获取当前页码
    # 获取当前页码前后各2页的页码范围
    page_range = list(range(max(current_page_num -1 , 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 1, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')

    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类的对应博客数量
    blog_types = BlogType.objects.annotate(blog_count=Count('blog'))     # 解析结果为SQL语句
    '''
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        # value
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        # key
        blog_dates_dict[blog_date] = blog_count


    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = blog_types  # 获取博客类型
    context['blog_dates'] = blog_dates_dict     # 获取日期归档
    return context


# 访问Blog列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request, 'zhijiadaren/blog_list.html', context)


# 访问Blog具体的页面
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()   # 上一篇博客
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()      # 下一篇博客
    context['blog'] = blog     # 当前博客
    response = render(request, 'zhijiadaren/blog_detail.html', context)  # 响应
    response.set_cookie(read_cookie_key, 'true')    # 阅读cookie标记
    return response


# 帅选博客系列
def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)   # 所有博客列表
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'zhijiadaren/blogs_with_type.html', context)


# 博客发布日期列表系列
def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)  # 按年月查询所有博客列表
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'zhijiadaren/blogs_with_date.html', context)
