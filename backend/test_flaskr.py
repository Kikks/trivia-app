import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["total_categories"])
        self.assertTrue(data["categories"])

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]) > 0)

    def test_search_with_result(self):
        search = "discovered"
        res = self.client().get("/questions?search={}".format(search))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]) > 0)

        for question in data["questions"]:
            search_term_is_contained_in_question = (
                search.lower() in question["question"].lower()
            )
            self.assertTrue(search_term_is_contained_in_question)

    def test_search_wihout_results(self):
        search = "asbfalsgkba glajbgaijebrhg"
        res = self.client().get("/questions?search={}".format(search))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])
        self.assertEqual(data["total_questions"], 0)
        self.assertTrue(len(data["questions"]) == 0)

    def test_delete_question(self):
        question_id = 5
        res = self.client().delete("/questions/{}".format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])

        deleted_question = Question.query.filter(
            Question.id == question_id
        ).one_or_none()

        self.assertFalse(deleted_question)

    def test_404_deleting_nonexisting_question(self):
        question_id = 10000
        res = self.client().delete("/questions/{}".format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_create_question(self):
        question = "Test question"
        answer = "This is the test answer"
        difficulty = 1
        category = 1

        res = self.client().post(
            "/questions",
            json={
                "question": question,
                "answer": answer,
                "difficulty": difficulty,
                "category": category,
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])

        new_question = Question.query.filter(
            Question.question == question,
            Question.answer == answer,
            Question.difficulty == difficulty,
            Question.category == category,
        ).one_or_none()

        if not new_question:
            self.fail("New question was not created.")

        self.assertTrue(new_question.format())

    def test_400_if_improper_question_is_submitted(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_get_questions_by_category(self):
        category = 1
        res = self.client().get("/categories/{}/questions".format(category))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["questions"]) > 0)

        for question in data["questions"]:
            self.assertEqual(question["category"], category)

    def test_get_404_filtering_questions_by_nonexisting_category(self):
        category = 10000
        res = self.client().get("/categories/{}/questions".format(category))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_quizzes(self):
        previous_questions = []
        quiz_category = {"id": 1, "type": "Science"}

        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": previous_questions,
                "quiz_category": quiz_category,
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], quiz_category["id"])

    def test_uniqueness_of_quizz(self):
        previous_questions = [2]
        quiz_category = {"id": 0, "type": ""}

        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": previous_questions,
                "quiz_category": quiz_category,
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["message"])
        self.assertTrue(data["question"])
        self.assertNotEqual(data["question"]["id"], quiz_category["id"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
