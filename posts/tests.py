from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post

User = get_user_model()

class BlogTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="bla@gmail.com",
            password="secret",
        )

        cls.post = Post.objects.create(
            author=cls.user,
            title="A good title",
            body="Nice body content",
        )

    def test_post_model(self):
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.title, 'A good title')
        self.assertEqual(self.post.body, 'Nice body content')
        self.assertEqual(str(self.post), 'A good title')


class PostAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user',
                                    password='userpassword')
        cls.admin_user = User.objects.create_superuser(
                                        username='admin',
                                    password='adminpassword'
        )                                    
        # post by non-admin user
        cls.post = Post.objects.create(
                        title='Sample Post',
                        author=cls.user,
                        body='Sample Body'
        )

        #URL for the list of posts
        cls.post_list_url = reverse('post_list')

        #URL for a detail post
        cls.post_detail_url = reverse('post_detail',
                                kwargs={'pk': cls.post.pk}
        )

    def test_list_unauthenticated(self):
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code,
                        status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        is_logged_in = self.client.login(username='user', 
                            password='userpassword')
        self.assertTrue(is_logged_in)
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)

    def test_list_admin(self):
        self.client.login(username='admin', 
                            password='adminpassword')
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)

    def test_detail_unauthenticated(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code,
                        status.HTTP_403_FORBIDDEN)
    
    def test_detail_authenticated_not_author(self):
        another_user = User.objects.create_user(
            username='anotheruser',
            password='password'
        )
        self.client.login(username='anotheruser', 
                            password='password')

        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)

    def test_detail_authenticated_author(self):
        self.client.login(username='user', 
                            password='userpassword')
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)

    def test_post_creation_as_authenicated(self):
        self.client.login(username='user', 
                            password='userpassword')
        response = self.client.post(self.post_list_url,
            {'title': 'new post', 'body': 'new content'}
            )
        self.assertEqual(response.status_code,
                        status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.latest('id').author,
                                self.user)

    def test_post_list_as_user(self):
        self.client.login(username='user', 
                            password='userpassword')
        response = self.client.get(self.post_list_url)
        self.assertTrue(
            len(response.data) == Post.objects.filter(author=self.user).count()
            )

    def test_post_list_as_admin(self):
        self.client.login(username='admin', 
                            password='adminpassword')
        response = self.client.get(self.post_list_url)
        self.assertTrue(len(response.data) == Post.objects.count())
            

    def test_update_post_authenticated_author(self):
        self.client.login(username='user', 
                    password='userpassword')
        update_data = {'title': 'updated post', 
                        'body': 'updated body'}
        response = self.client.put(self.post_detail_url, 
                                    update_data)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)
        self.assertEqual(Post.objects.last().title, 'updated post')
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'updated post')

    def test_update_post_authenticated_not_author(self):
        another_user = User.objects.create_user(
            username='anotheruser',
            password='password'
        )
        self.client.login(username='anotheruser', 
                            password='password')
                            
        update_data = {'title': 'updated post', 
                        'body': 'updated body'}
        response = self.client.put(self.post_detail_url,
                                    update_data)
        self.assertEqual(response.status_code,
                        status.HTTP_403_FORBIDDEN)
    
    def test_update_post_authenticated_admin(self):
        self.client.login(username='admin', 
                    password='adminpassword')
        update_data = {'title': 'updated post', 
                        'body': 'updated body'}
        response = self.client.put(self.post_detail_url, 
                                    update_data)
        self.assertEqual(response.status_code,
                        status.HTTP_200_OK)
        self.assertEqual(Post.objects.last().title, 'updated post')
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'updated post')
                                
    def test_delete_post_authenticated_author(self):
        self.client.login(username='user', 
                    password='userpassword')
        response = self.client.delete(self.post_detail_url) 
        self.assertEqual(response.status_code,
                        status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Post.objects.filter(pk=self.post.pk).exists()
            )
                                    
    def test_delete_post_authenticated_not_author(self):
        another_user = User.objects.create_user(
            username='anotheruser',
            password='password'
        )
        self.client.login(username='anotheruser', 
                            password='password')
        response = self.client.delete(self.post_detail_url) 
        self.assertEqual(response.status_code,
                        status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Post.objects.filter(pk=self.post.pk).exists()
            )

    def test_delete_post_admin(self):
        self.client.login(username='admin', 
                    password='adminpassword')
        response = self.client.delete(self.post_detail_url) 
        self.assertEqual(response.status_code,
                        status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Post.objects.filter(pk=self.post.pk).exists()
            )
