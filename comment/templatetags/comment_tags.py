from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm

register = template.Library()


# 获取评论的数量
@register.simple_tag
def get_comment_count(obj):
    # obj为从模板传过来的blog参数
    content_type = ContentType.objects.get_for_model(obj)
    # 统计评论数量
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()


@register.simple_tag
def get_comment_form(obj):
    # obj为从模板传过来的blog参数
    content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={
        'content_type': content_type.model,
        'object_id': obj.pk,
        'reply_comment_id': 0})
    return form


# 获取评论的列表
@register.simple_tag
def get_comment_list(obj):
    # obj为从模板传过来的blog参数
    content_type = ContentType.objects.get_for_model(obj)
    # 当前评论
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('-comment_time')
