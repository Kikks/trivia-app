import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_table(page, limit, selection):
    start = (page - 1) * limit
    end = start + limit

    records = [record.format() for record in selection]
    current_records = records[start:end]

    return current_records


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def get_categories():
        try:
            categories = {}

            all_categories = [item.format() for item in Category.query.all()]

            for category in all_categories:
                categories["{}".format(category["id"])] = category["type"]

            return jsonify(
                {
                    "success": True,
                    "message": "Categories fetched successfully.",
                    "categories": categories,
                    "total_categories": len(categories),
                }
            )
        except Exception as error:
            print(error)
            abort(500)

    @app.route("/questions")
    def get_questions():
        try:
            page = request.args.get("page", 1, type=int)
            search = request.args.get("search", "", type=str)
            questions = (
                Question.query.filter(
                    func.lower(Question.question).like("%{}%".format(search.lower())),
                )
                .order_by(Question.id.desc())
                .paginate(page=page, per_page=QUESTIONS_PER_PAGE, error_out=True)
            )

            categories = {}
            all_categories = [item.format() for item in Category.query.all()]
            for category in all_categories:
                categories["{}".format(category["id"])] = category["type"]

            return jsonify(
                {
                    "success": True,
                    "message": "Questions fetched successfully.",
                    "questions": [question.format() for question in questions.items],
                    "total_questions": questions.total,
                    "categories": categories,
                    "current_category": "All",
                }
            )
        except Exception as error:
            print(error)
            abort(404)

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if not question:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "message": "Question with id: {} deleted successfully.".format(
                        question_id
                    ),
                }
            )

        except Exception as error:
            print(error)
            abort(404)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)

        if (not question) or (not answer) or (not difficulty) or (not category):
            abort(400)

        try:
            existing_category = Category.query.filter(
                Category.id == category
            ).one_or_none()

            if not existing_category:
                abort(400)

            question = Question(question, answer, difficulty, category)
            question.insert()

            return jsonify(
                {
                    "success": True,
                    "message": "New question created successfully.",
                }
            )

        except Exception as error:
            print(error)
            abort(400)

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        try:
            page = request.args.get("page", 1, type=int)

            existing_category = Category.query.filter(
                Category.id == category_id
            ).one_or_none()

            if not existing_category:
                abort(400)

            questions = (
                Question.query.filter(Question.category == category_id)
                .order_by(Question.id.desc())
                .all()
            )

            paginated_questions = paginate_table(page, QUESTIONS_PER_PAGE, questions)

            if not len(questions) == 0 and len(paginated_questions) == 0:
                abort(404)

            categories = {}
            all_categories = [item.format() for item in Category.query.all()]
            for category in all_categories:
                categories["{}".format(category["id"])] = category["type"]

            return jsonify(
                {
                    "success": True,
                    "message": "Questions fetched successfully.",
                    "questions": paginated_questions,
                    "total_questions": len(questions),
                    "categories": categories,
                    "current_category": existing_category.format()["type"],
                }
            )
        except Exception as error:
            print(error)
            abort(404)

    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        try:
            body = request.get_json()

            previous_questions = body.get("previous_questions", [])
            quiz_category = body.get("quiz_category", {"id": 0})

            question = None

            if quiz_category["id"] == 0:
                question = (
                    Question.query.filter(
                        ~Question.id.in_(previous_questions),
                    )
                    .order_by(func.random())
                    .first()
                )
            else:
                question = (
                    Question.query.filter(
                        ~Question.id.in_(previous_questions),
                        Question.category == quiz_category["id"],
                    )
                    .order_by(func.random())
                    .first()
                )

            return jsonify(
                {
                    "success": True,
                    "message": "Questions fetched successfully.",
                    "question": question.format() if question else None,
                }
            )
        except Exception as error:
            print(error)
            abort(404)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found."}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad Request."}), 400

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Server error."}),
            500,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable."}),
            422,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method not allowed."}),
            405,
        )

    return app
