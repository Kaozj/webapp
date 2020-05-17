import os
import unittest

from views import app,db
from _config import basedir
from models import User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):
	def setUp(self):
		app.config['TESTING']=True
		app.config['WTF_CSRF_ENABLED']=False
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
		app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir,TEST_DB)
		self.app=app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def create_user(self,name,email,password):
		new_user= User(name=name,email=email,password=password)
		db.session.add(new_user)
		db.session.commit()

	def create_task(self):
		return self.app.post('add/',data = dict(
			name = "Go to sleep"
			,due_date = "10/10/2099"
			,priority = '1'
			,posted_date = "10/10/2098"
			,status = '1'
		),follow_redirects=True)

	def login(self,name,password):
		return self.app.post('/',data=dict(name=name,password=password),follow_redirects = True)

	def logout(self):
		return self.app.get('logout/',follow_redirects=True)

	def create_admin_user(self):
		new_user = User(
			name='Superman',
			email='admin@realpython.com',
			password='allpowerful',
			role='admin'
			)
		db.session.add(new_user)
		db.session.commit()

	def test_users_can_add_tasks(self):
		self.create_user('Michale','mike@realpython.com','python')
		self.login('Michale','python')
		self.app.get('tasks/',follow_redirects=True)
		response=self.create_task()
		self.assertIn(b'New entry created',response.data)

	def test_users_cannot_add_tasks_when_error(self):
		self.create_user('Michale','mike@realpython.com','python')	
		self.login('Michale','python')
		self.app.get('tasks',follow_redirects=True)
		response=self.app.post('add/',data=dict(
			name = "Go to sleep"
			,due_date = " "
			,priority = '1'
			,posted_date = "10/10/2098"
			,status = '1'	
			),follow_redirects=True)
		self.assertIn(b'This field is required.',response.data)

	def test_users_can_complete_tasks(self):
		self.create_user('qweqwe','qweqwe@gmail.com','python')
		self.login('qweqwe','python')
		self.app.get('tasks/',follow_redirects=True)
		self.create_task()	
		response = self.app.get('complete/1/',follow_redirects=True)
		self.assertIn(b'Task marked complete',response.data)

	def test_users_can_delete_tasks(self):
		self.create_user('qweqwe','qweqwe@gmail.com','python')
		self.login('qweqwe','python')
		self.app.get('tasks/',follow_redirects=True)
		self.create_task()	
		response = self.app.get('delete/1/',follow_redirects=True)
		self.assertIn(b'Task deleted',response.data)

	def test_users_cannot_complete_tasks_not_created_by_them(self):
		self.create_user('zijiankao','zijiankao@gmail.com','python')
		self.login('zijiankao','python')
		self.app.get('tasks/',follow_redirects=True)
		self.create_task()		
		self.logout()
		self.create_user('shiankao','shiankao@gmail.com','python')
		self.login('shiankao','python')
		self.app.get('tasks/',follow_redirects=True)
		response=self.app.get("complete/1/",follow_redirects=True)
		self.assertNotIn(b'Task marked complete',response.data)
		self.assertIn(b'You can only update tasks that belong to you',response.data)

	def test_users_cannot_delete_tasks_not_created_by_them(self):
		self.create_user('zijiankao','zijiankao@gmail.com','python')
		self.login('zijiankao','python')
		self.app.get('tasks/',follow_redirects=True)
		self.create_task()		
		self.logout()
		self.create_user('shiankao','shiankao@gmail.com','python')
		self.login('shiankao','python')
		self.app.get('tasks/',follow_redirects=True)
		response=self.app.get("delete/1/",follow_redirects=True)
		self.assertIn(b'You can only delete tasks that belong to you',response.data)		

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only update tasks that belong to you.', response.data
        )

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only delete tasks that belong to you.', response.data
        )
