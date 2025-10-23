from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.post = Post.objects.create(
            author=cls.user,
            title='Test Post',
            content='This is a test post'
        )

    def test_post_content(self):
        post = Post.objects.get(id=1)
        expected_author = f'{post.author}'
        expected_title = f'{post.title}'
        expected_content = f'{post.content}'
        self.assertEqual(expected_author, 'testuser')
        self.assertEqual(expected_title, 'Test Post')
        self.assertEqual(expected_content, 'This is a test post')

    def test_post_str(self):
        post = Post.objects.get(id=1)
        self.assertEqual(str(post), post.title)

    def test_get_absolute_url(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.get_absolute_url(), reverse('post-detail', args=[post.id]))

class PostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='This is a test post'
        )

    def test_post_list_view(self):
        url = reverse('blog-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test post')
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_post_detail_view(self):
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.content)
    
    def test_create_post_view(self):        
        self.client.login(username='testuser', password='12345')
        url = reverse('post-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        response = self.client.post(url, {
            'title': 'New title',
            'content': 'New Content'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New title').exists())

    def test_update_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        response = self.client.post(url, {
            'title': 'New title - updated',
            'content': 'New Content - updated'
        })
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New title - updated').exists())

    def test_delete_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())



