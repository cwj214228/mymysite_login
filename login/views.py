from django.shortcuts import render, redirect
from . import models
from .forms import UserForm, RegisterForm
import hashlib

'''主页视图'''
def index(request):
    pass
    return render(request, 'login/index.html')

'''用户登陆视图'''
def login(request):
    # 从session里面的is_login判断是否已经登陆
    if request.session.get('is_login', None):
        return redirect("/index/")
    # 如果访问index用的是POST方法，则执行下面的语句
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        # 判断表单里面的数据是不是有效的，有效就执行下面的代码，它暂时还没有访问数据库的
        if login_form.is_valid():
            # 获取表单里的username和password
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                # 通过username，获取数据库中对应的的数据，保存在对象user中
                user = models.User.objects.get(name=username)
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对，数据库中的用户密码已经被哈希加密了
                    # 若密码正确，设置session里面的is_login为True，下面也差不多一样的道理
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())
    # 以上是POST请求才会执行的代码

    # GET请求就执行下面的两句代码
    login_form = UserForm()
    return render(request, 'login/login.html', locals())

'''用户注册视图'''
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        # 获取注册的表单，把表单内容封装再一个register_form对象里面
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 判断数据是不是有效的，有效就继续往下执行
            # 从register_form对象中提取想要的数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                # 根据用户名，查一下数据库中有没有关于这个用户名的数据
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                # 根据email，查一下数据库中有没有关于这个email的数据
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
            # 以上是POST请求执行的代码

    # 如果是GET请求，就执行下面的两句
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

'''退出登陆的视图'''
def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/index/')
    # 清除服务器里面关于这个用户的session数据
    request.session.flush()
    return redirect('/index/')

'''用户密码加密方法，哈希加密'''
def hash_code(s, salt='mysite_login'):
    h = hashlib.sha256()
    # 把用户的密码加上'mysite_login'，再进行哈希
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()  #返回哈希后的值