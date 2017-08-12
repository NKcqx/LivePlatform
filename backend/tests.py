from django.test import TestCase,Client
from backend.myview import room_view,user_view,toolkits
from backend.models import LiveRoom,User
from django.utils import timezone
from django.forms.models import model_to_dict
from backend.models import User,Punishment,LiveRoom
from backend.myview.user_view import random_str
from backend.myview.user_view import test_phone
from backend.myview.user_view import test_email
from backend.myview.user_view import create_user_folder
from backend.myview.user_view import getUser
from backend.myview.user_view import sendTo
from backend.myview.user_view import signupSubmit
from backend.myview.user_view import loginSubmit
from backend.myview.user_view import testUsername
from backend.myview.user_view import changeAvatar
from backend.myview.user_view import changeGenderAndNickname
from backend.myview.user_view import changePassword
from backend.myview.user_view import getUserFromSession
from backend.myview.punishment_base import banSpeakOne
from backend.myview.punishment_base import banSpeakPublic
from backend.myview.punishment_base import outOne
from backend.myview.punishment_base import clean_table
from backend.myview.punishment_base import is_out
from backend.myview.punishment_base import is_ban_speak
from django.contrib import auth
import os
import re
import json

# Create your tests here.
class UserTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user1=User.objects.create_user(username='HIHA',password='1234',phone='15302178925')
        self.user2=User.objects.create_user(username='baobao',password='1234',phone='15222856278')
        self.user3=User.objects.create_user(username='xiaolaotou',password='1234',phone='13752652469')
        self.user4=User.objects.create_user(username='chenqixiang',password='1234',email='892670992@qq.com')
    def test_create_user(self):
        self.assertEqual(self.user1.avatar,'frontend/static/users/avatar.jpg')
        self.assertEqual(self.user1.role,'S')
        self.assertEqual(self.user1.phone,'15302178925')
        self.assertEqual(self.user1.gender,True)
        self.assertEqual(self.user4.phone,None)
        self.assertEqual(self.user1.email,'')
    def test_random_str(self):
        self.assertEqual(len(random_str()),4)
        self.assertEqual(len(random_str(5)),5)
        self.assertTrue(random_str().isdigit())
    def test_test_email(self):
        self.assertTrue(test_email('15302178925@163.com'))
        self.assertTrue(test_email('2020263746@qq.com'))
        self.assertTrue(test_email('dongbaobao94@gmail.com'))
    def test_test_phone(self):
        self.assertTrue(test_phone('15302178925'))
        self.assertTrue(test_phone('15222856278'))
        self.assertTrue(test_phone('13752652469'))
        self.assertTrue(test_phone('13662197063'))
    def test_create_user_folder(self):
        self.assertTrue(create_user_folder('23'))
        self.assertTrue(create_user_folder('22'))
        self.assertEqual(create_user_folder('892670995@qq.com'),False)
        self.assertEqual(create_user_folder('13513616853'),False)
class RoomViewTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        user_dic = {"username":"15032002730","phone":"15032002730", "password":"cqx1997215"}
        user_json = json.dumps(user_dic)
        self.c.post('/signup/',user_json, content_type = "application/json")
        user = User.objects.create_user(
            username = "15032002730",
            phone = "15032002730",
            password = "cqx1997215",
            role = "T"
            )
        user.save()
        user_json = json.dumps({"username":"15032002730","password":"cqx1997215"})
        self.c.post('/login/', user_json, content_type = "application/json")
        pass
    def test_create_folder(self):
        room_view.create_folder("unittest")
        self.assertTrue(os.path.exists("frontend/static/rooms/unittest"))
        self.assertTrue(os.path.isdir("frontend/static/rooms/unittest"))
        self.assertTrue(os.path.isfile("frontend/static/rooms/unittest/log.txt"))
    def test_create_get_end_room(self):
        room = {"name" : "test_room1"}
        res = self.c.post('/createroom/',room)
        self.assertEqual(res.status_code, 200)
        res = self.c.post('/endroom/',{})
        self.assertTrue(res.status_code, 200)

        room = {"name" : "test_room2", "is_silence" : "true"}
        res = self.c.post('/createroom/',room)
        self.assertEqual(res.status_code, 200)
        res = self.c.post('/endroom/',{})
        self.assertEqual(res.status_code, 200)

        #test the trigger
        room = {"name" : "test_room3"}
        res = self.c.post('/createroom/', room)
        room = LiveRoom.objects.get(name = "test_room3")
        self.assertFalse(room.is_silence)
        self.assertTrue(room.end_time is None)

        req = {'audience_amount' : '999'}
        req = json.dumps(req)
        res = self.c.post('/updateroom/', req, content_type = "application/json")
        room = LiveRoom.objects.get(name = 'test_room3')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(room.audience_amount, 999)

        req = {'name' : 'new_room_name'}
        req = json.dumps(req)
        res = self.c.post('/updateroom/', req, content_type = "application/json")
        rooms = LiveRoom.objects.filter(name = 'new_room_name')
        self.assertTrue(len(rooms) > 0)
        self.assertEqual(rooms[0].name, 'new_room_name')

        req = {}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(content['rooms']), 3)
        req = {"id" : "1"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 1)
        req = {"order_by":"name"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 3)
        req = {"is_living" : "true"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 1)
        req = {"is_living" : "false"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 2)
        req = {"limit" : "2"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 2)
        req = {"limit" : "3","start": "1"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 2)
        req = {"limit" : "3","start": "2"}
        res = self.c.get('/getroom/', req)
        content = json.loads(res.content.decode('utf8'))
        self.assertEqual(len(content['rooms']), 1)
    def tearDown(self):
        pass

class ToolkitsTestCase(TestCase):
    def setUp(self):
        pass
    def test_encode_json(self):
        result = toolkits.encode_json("json")
        self.assertEqual(type(result), type("string"))
        result = toolkits.encode_json(timezone.now())
        self.assertEqual(type(result), type("string"))
        result = toolkits.encode_json(123)
        self.assertEqual(result, "123")
        self.assertEqual(type(result), type("10"))
        result = toolkits.encode_json(True)
        self.assertTrue(result)

    def tearDown(self):
        pass