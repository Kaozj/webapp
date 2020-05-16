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

	def test_user_can_register(self):
		new_user = User("zzzzzzz","zzzzzzz@gmail.com","zijiankao")
		db.session.add(new_user)
		db.session.commit()
		test = db.session.query(User).all()
		for t in test:
			t.name
		assert t.name == 'zzzzzzz'

	def test_form_is_present(self):
	 	response = self.app.get('/')
	 	self.assertEqual(response.status_code,200)
	 	self.assertIn(b'Please sign in to access your task list',response.data)

	def login(self,name,password):
		return self.app.post('/',data=dict(name=name,password=password),follow_redirects = True)

	def test_user_cannot_login_unless_registered(self):
		response=self.login('foo','bar')
		self.assertIn(b'Invalid username or password',response.data)

	def register(self,name,email,password,confirm):
		return self.app.post(
			'register/',
			data = dict(name=name,email=email,password=password,confirm=confirm),	
			follow_redirects=True
			)

	def test_users_can_login(self):
		self.register('qweqwe','qweqwe@gmail.com','python','python')
		response = self.login('qweqwe','python')
		self.assertIn(b'Welcome!',response.data)

	def logout(self):
		return self.app.get('logout/',follow_redirects=True)	

	def test_logged_in_users_can_logout(self):
		self.register('eykhoda','khoda@gmail.com','python101','python101')
		self.login('eykhoda','python101')
		response=self.logout()
		self.assertIn(b'Bye Bye',response.data)

	def test_not_logged_in_users_cannot_logout(self):
		response=self.logout()
		self.assertNotIn(b'Bye Bye',response.data)


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


	def test_users_can_add_tasks(self):
		self.create_user('Michale','mike@realpython.com','python')
		self.login('Michale','python')
		self.app.get('tasks',follow_redirects=True)
		response=self.create_task()
		self.assertIn(b'New entry created',response.data)


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




if __name__ == '__main__':
	unittest.main()

