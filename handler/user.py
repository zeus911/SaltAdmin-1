#!/usr/bin/python
# -*- coding:utf-8 -*-
# Powered By KStudio
# 用户管理

from BaseHandler import BaseHandler
from tornado.web import authenticated as Auth
from model.models import User

class UserHandler(BaseHandler):
    @Auth
    def get(self):
        data = self.db.query(User).all()
        gender = {1:'男', 2:'女'}
        self.render('user/index.html', title="用户管理",data=data,gender=gender)

# 用户登录
class LoginHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if user:
            return self.redirect('/') # 已登录则跳转到首页
        self.render('user/login.html', title="Login")

    def post(self):
        username = self.get_argument("username",None)
        password = self.get_argument("password",None)
        remember = self.get_argument("remember","no")
        if not username or not password:
            return self.jsonReturn({'code':-1,'msg':'参数错误'})
        user = self.db.query(User).filter_by(username=username).first()
        if not user:
            return self.jsonReturn({'code': -2, 'msg': '用户名或密码错误'})
        if self.md5(password) != user.password:
            return self.jsonReturn({'code': -2, 'msg': '用户名或密码错误'})
        ##### 验证通过逻辑 #####
        # 记录登录信息
        headers = self.request.headers
        login_ua = headers.get('User-Agent')
        login_ip = self.request.remote_ip
        login_data = {
            "login_time": self.time,
            "login_ua": login_ua,
            "login_ip": login_ip
            # "login_location": user.login_location
        }
        self.db.query(User).filter_by(id=user.id).update(login_data)
        self.db.commit()
        # 写Session
        session = {
            "uid": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "login_time": user.login_time,
            "login_ua": user.login_ua,
            "login_ip": user.login_ip,
            "login_location": user.login_location
        }
        self.create_session(session) # 创建Session
        url = self.get_argument("next","/")
        return self.jsonReturn({'code': 0, 'msg': 'Success', 'url': url})


# 注销登录
class LogoutHandler(BaseHandler):
    def get(self):
        self.remove_session()
        self.redirect(self.get_login_url())


# 我的资料
class ProfileHandler(BaseHandler):
    @Auth
    def get(self):
        user = self.current_user
        uid = user['uid']
        profile = self.db.query(User).filter_by(id=uid).first()
        self.render('user/profile.html',profile=profile)

    @Auth
    def post(self):
        data = {
            "nickname": self.get_argument("nickname", None),
            "gender": self.get_argument("gender", None),
            "email": self.get_argument("email", None),
            "phone": self.get_argument("phone", None),
            "dept": self.get_argument("dept", None),
            "update_time": self.time
        }
        # 数据校验
        if not data['nickname']:
            return self.jsonReturn({'code': -1, 'msg': '姓名不能空'})
        if data['gender'] not in ['1','2']:
            return self.jsonReturn({'code': -1, 'msg': '参数错误'})
        user = self.current_user
        self.db.query(User).filter_by(id=user['uid']).update(data) # <type 'long'> - 1
        self.db.commit() # <type 'NoneType'> - None
        return self.jsonReturn({'code': 0, 'msg': 'Success'})


# 修改密码
class PasswdHandler(BaseHandler):
    @Auth
    def get(self):
        self.render('user/passwd.html')