from django.test import TestCase

class ReviewTestCase(TestCase):

    def test_list_view(self):
        response = self.client.get('reviews/review-list/')
        self.assertEqual(response.status_code, 200)
