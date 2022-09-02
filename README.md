# Udacity Trivia App Documentation

## Trivia App

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

I have helped create API endpoints and integrated them to make the trivia app functional. The application has the following functionalities:

1. Display questions - Questions are displayed with their categories, difficulty ratings and their answers can be revealed or left hidden. The questions can also be filtered by their respective categories.

2. Delete questions - Questions can be deleted.

3. Add questions - New questions can be added to the application's database. The questions are validated and must include question and answer texts.

4. Search for questions based on a text query string - Questions can be filtered by a text query string and only questions that have the query string as substrings will be displayed. The search is case insensitive.

5. Play the quiz game - Questions are randomly selected and displayed. A user of the application can choose to have questions from all categories or a specific category.



## Project Structure

The application is broken down into two broad sections which are:

### Backend

The [backend](./backend/README.md) directory contains all the server code for this appication. The API routes definitions, tests and models can be found in the following files respectively:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`
3. `backend/models.py`

> View the [Backend README](./backend/README.md) for a proper documentation of the API.

### Frontend

The [frontend](./frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server. The screens for this application are defined in the following files:


1. `frontend/src/components/QuestionView.js`
2. `frontend/src/components/FormView.js`
3. `frontend/src/components/QuizView.js`


> View the [Frontend README](./frontend/README.md) for a proper documentation of the Frontend application.
