import os
import unittest

from project import app,db,bcrypt
from project._config import basedir
from project.models import Task,User

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
		new_user = User("zzzzzzz","zzzzzzz@gmail.com",bcrypt.generate_password_hash("zijiankao"))
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
		self.assertIn(b'Goodbye!',response.data)

	def test_not_logged_in_users_cannot_logout(self):
		response=self.logout()
		self.assertNotIn(b'Goodbye!',response.data)

	def test_logged_in_users_can_access_tasks_page(self):
		self.register('eykhoda','khoda@gmail.com','python101','python101')
		self.login('eykhoda','python101')
		response=self.app.get('tasks/')
		self.assertEqual(response.status_code,200)
		self.assertIn(b'Add a new task:',response.data)
		self.logout()
		response=self.app.get('tasks/',follow_redirects=True)
		self.assertIn(b'You need to login first.',response.data)


	def test_default_user_role(self):

		db.session.add(User("Johnny","john@doe.com","johnny"))
		db.session.commit()
		users = db.session.query(User).all()
		print(users)
		for user in users:
			self.assertEqual(user.role, 'user')

	def test_task_template_displays_logged_in_user_name(self):
		self.register('eykhoda','khoda@gmail.com','python101','python101')
		self.login('eykhoda','python101')
		response=self.app.get('tasks/',follow_redirects=True)
		self.assertIn(b'eykhoda',response.data)


if __name__ == '__main__':
	unittest.main()

