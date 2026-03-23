# Library-Management-System
Library Book Management System
A web-based library book management system built with Python Flask and MySQL. Allows a librarian to manage book records through a simple browser interface running locally.
Features:

Dashboard with live stats showing total books, copies, available, and out of stock count
Add new books with input validation and duplicate ISBN check
View all books in a sortable paginated table
Edit existing book details through a pre-filled form
Delete books with a confirmation prompt
Search books by title, author, category, or ISBN

Tech Stack

Python 3
Flask
MySQL
mysql-connector-python
HTML / CSS

Setup

1. Clone the repo
2. Install dependencies with pip install flask mysql-connector-python
3. Import setup.sql into MySQL Workbench
4. Add your MySQL password in app.py
5. Run with python app.py
6. Open http://127.0.0.1:5000 in your browser
