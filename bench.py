from locust import FastHttpUser, task


class HelloWorldUser(FastHttpUser):
    @task
    def hello_world(self):
        self.client.get("/blog/2/blog-content")
