import unittest
from app import app, db
from database import User, UserProgress

class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # ---------------- HOME PAGE ----------------
    def test_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"HandSpeak", res.data)

    # ---------------- REGISTER + LOGIN ----------------
    def test_user_registration_and_login(self):
        # Register
        self.client.post("/register", data={
            "username": "testuser",
            "email": "test@test.com",
            "password": "1234"
        })

        # Login
        res = self.client.post("/login", data={
            "username": "testuser",
            "password": "1234"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)

    # ---------------- SAVE SCORE ----------------
    def test_save_progress(self):
        with app.app_context():
            entry = UserProgress(username="tester", score=7)
            db.session.add(entry)
            db.session.commit()

            saved = UserProgress.query.first()
            self.assertEqual(saved.username, "tester")
            self.assertEqual(saved.score, 7)

    # ---------------- QUIZ API ----------------
    def test_quiz_question_api(self):
        res = self.client.get("/quiz_question")
        self.assertEqual(res.status_code, 200)
        self.assertIn("letter", res.get_json())

    # ---------------- ADMIN DASHBOARD ----------------
    def test_admin_dashboard(self):
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 200)

    # ---------------- VIDEO FEED ----------------
    def test_video_feed(self):
        res = self.client.get("/video_feed")
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
