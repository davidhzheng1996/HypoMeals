from django.test import TestCase
from models import Ingredient, Sku

# Allow django to create database:
# https://stackoverflow.com/questions/14186055/django-test-app-error-got-an-error-creating-the-test-database-permission-deni


class IngredientViewTests(TestCase):
    def test_add_ingredient(self):
        Ingredient.objects.create(ingredient_name='carrot', description='healthy', 
            package_size='40oz', cpp=30)
        response = self.client.get(reverse('ingredients:index'))
        print(response.context)

    # def test_no_questions(self):
    #     """
    #     If no questions exist, an appropriate message is displayed.
    #     """
    #     response = self.client.get(reverse('polls:index'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "No polls are available.")
    #     self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # def test_past_question(self):
    #     """
    #     Questions with a pub_date in the past are displayed on the
    #     index page.
    #     """
    #     create_question(question_text="Past question.", days=-30)
    #     response = self.client.get(reverse('polls:index'))
    #     self.assertQuerysetEqual(
    #         response.context['latest_question_list'],
    #         ['<Question: Past question.>']
    #     )

    # def test_future_question(self):
    #     """
    #     Questions with a pub_date in the future aren't displayed on
    #     the index page.
    #     """
    #     create_question(question_text="Future question.", days=30)
    #     response = self.client.get(reverse('polls:index'))
    #     self.assertContains(response, "No polls are available.")
    #     self.assertQuerysetEqual(response.context['latest_question_list'], [])

    # def test_future_question_and_past_question(self):
    #     """
    #     Even if both past and future questions exist, only past questions
    #     are displayed.
    #     """
    #     create_question(question_text="Past question.", days=-30)
    #     create_question(question_text="Future question.", days=30)
    #     response = self.client.get(reverse('polls:index'))
    #     self.assertQuerysetEqual(
    #         response.context['latest_question_list'],
    #         ['<Question: Past question.>']
    #     )

    # def test_two_past_questions(self):
    #     """
    #     The questions index page may display multiple questions.
    #     """
    #     create_question(question_text="Past question 1.", days=-30)
    #     create_question(question_text="Past question 2.", days=-5)
    #     response = self.client.get(reverse('polls:index'))
    #     self.assertQuerysetEqual(
    #         response.context['latest_question_list'],
    #         ['<Question: Past question 2.>', '<Question: Past question 1.>']
    #     )