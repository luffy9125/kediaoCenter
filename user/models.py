from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, verbose_name='昵称')

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


# 动态绑定
# 获取昵称
def get_nickname(self):
    # 如果nickname自身存在
    if Profile.objects.filter(user=self).exists():
        # 实例化
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''


# 动态绑定
# 获取昵称或用户名
def get_nickname_or_username(self):
    # 如果nickname自身存在
    if Profile.objects.filter(user=self).exists():
        # 实例化
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username


# 判断nickname是否为空
def has_nickname(self):
    return Profile.objects.filter(user=self).exists()


User.get_nickname = get_nickname
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname