# > locust -f test.py --host http://localhost:8000
from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/blog/2/blog-content")
