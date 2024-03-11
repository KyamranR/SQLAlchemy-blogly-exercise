import unittest
from app import app, db, User, Post

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_redirect_to_user(self):
        with app.app_context():
            response = self.client.get('/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers['Location'], '/users')

    def test_list_users(self):
        with app.app_context():
            user1 = User(first_name='Alice', last_name='Smith')
            user2 = User(first_name='John', last_name='Wick')
            db.session.add_all([user1, user2])
            db.session.commit()

            response = self.client.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Alice Smith', response.data)
            self.assertIn(b'John Wick', response.data)
    
    def test_add_user(self):
        with app.app_context():
            response = self.client.post('/users/new', data={'first_name': 'Kyamran', 'last_name': 'Riza', 'image_url': 'https://akm-img-a-in.tosshub.com/indiatoday/images/story/media_bank/202309/elon-musk-252648408-16x9.jpg?VersionId=9KYZpqpoY3WvH8eVZg54mmkpTGfvPCWj&size=690:388'})
            self.assertEqual(response.status_code, 302)
            user = User.query.filter_by(first_name='Kyamran', last_name='Riza').first()
            self.assertIsNotNone(user)

    def test_show_user(self):
        with app.app_context():
            user = User(first_name='Kyamran', last_name='Riza', image_url='https://akm-img-a-in.tosshub.com/indiatoday/images/story/media_bank/202309/elon-musk-252648408-16x9.jpg?VersionId=9KYZpqpoY3WvH8eVZg54mmkpTGfvPCWj&size=690:388')
            db.session.add(user)
            db.session.commit()
            response = self.client.get(f'/users/{user.id}')
            self.assertIn(b'Kyamran Riza', response.data)

    def test_edit_user(self):
        with app.app_context():
            user = User(first_name='Kyamran', last_name='Riza', image_url='https://akm-img-a-in.tosshub.com/indiatoday/images/story/media_bank/202309/elon-musk-252648408-16x9.jpg?VersionId=9KYZpqpoY3WvH8eVZg54mmkpTGfvPCWj&size=690:388')
            db.session.add(user)
            db.session.commit()
            response = self.client.post(f'/users/{user.id}/edit', data={'first_name': 'James', 'last_name': 'Bond', 'image_url': 'https://example.com/updated_image.jpg'})
            self.assertEqual(response.status_code, 302)
            updated_user = User.query.get(user.id)
            self.assertEqual(updated_user.first_name, 'James')
            self.assertEqual(updated_user.last_name, 'Bond')

    def test_delete_user(self):
        with app.app_context():
            user = User(first_name= 'Kyamran', last_name='Riza', image_url='https://akm-img-a-in.tosshub.com/indiatoday/images/story/media_bank/202309/elon-musk-252648408-16x9.jpg?VersionId=9KYZpqpoY3WvH8eVZg54mmkpTGfvPCWj&size=690:388')
            db.session.add(user)
            db.session.commit()
            response = self.client.post(f'/users/{user.id}/delete')
            self.assertEqual(response.status_code, 302)
            self.assertIsNone(User.query.get(user.id))



class TestPost(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            

    def test_add_post(self):
        with app.app_context():
            user = User(first_name='Jane', last_name='Smith')
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/users/{user.id}/posts/new', data={'title': 'Test Title', 'content': 'This is a test post'})
            self.assertEqual(response.status_code, 302)
            new_post = Post.query.filter_by(title='Test Title').first()
            self.assertIsNotNone(new_post)
            self.assertEqual(new_post.user_id, user.id)

    def test_show_post(self):
        with app.app_context():
            user = User(first_name='Jane', last_name='Smith')
            db.session.add(user)
            db.session.commit()
            post = Post(title='Test Title', content='This is a test post', user_id=user.id)
            db.session.add(post)
            db.session.commit()

            response = self.client.get(f'/posts/{post.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Title', response.data)


    def test_edit_post(self):
        with app.app_context():
            user = User(first_name='Jane', last_name='Smith')
            db.session.add(user)
            db.session.commit()
            post = Post(title='Test Title', content='This is a test post', user_id=user.id)
            db.session.add(post)
            db.session.commit()
            response = self.client.post(f'/posts/{post.id}/edit', data={'title': 'Updated Title', 'content': 'Updated This is a test post'})
            self.assertEqual(response.status_code, 302)
            updated_post = Post.query.get(post.id)
            self.assertEqual(updated_post.title, 'Updated Title')
            self.assertEqual(updated_post.content, 'Updated This is a test post')


    def test_delete_post(self):
        with app.app_context():
            user = User(first_name='Jane', last_name='Smith')
            db.session.add(user)
            db.session.commit()
            post = Post(title='Test Title', content='This is a test post', user_id=user.id)
            db.session.add(post)
            db.session.commit()

            response = self.client.post(f'/posts/{post.id}/delete')
            self.assertEqual(response.status_code, 302)
            self.assertIsNone(Post.query.get(post.id))




if __name__ == '__main__':
    unittest.main()