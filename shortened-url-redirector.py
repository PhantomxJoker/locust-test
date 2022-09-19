from locust import HttpUser, task, between
import os
from dotenv import load_dotenv
import random
import json
from os.path import exists

load_dotenv('.env')

lower_time_limit = 3.0
upper_time_limit = 7.0

class ShortenedUrl(HttpUser):
    wait_time = between(lower_time_limit, upper_time_limit)
    host = os.environ.get('host')
    path_base = os.environ.get('path-base')
    shortened_url_path = os.environ.get('path-shortened-urls')

    def randomFromFile(self, instance = "shortened-urls"):
        try:
            files = os.listdir(self.path_base + instance)
            if len(files) < 1:
                return 0

            filename = files[random.randint(0, len(files) - 1)]
            f = open(self.path_base + instance + "/" + filename, "r")
            item_data = f.read()
            return item_data
        except:
            return "error randomFromFile"

    @task(1)
    def getShortenedUrlToRedirect(self):
        try:
            shortened_info = self.randomFromFile("shortened-urls")
            if shortened_info != 0:
                headers = { "Content-Type": "application/json" }
                shortened_list = str(shortened_info).split(";")
                if bool(shortened_list):
                    shortened_id = shortened_list[2]

                    rs = self.client.get("/{0}".format(shortened_id),
                    headers=headers,
                    name="/getShortenedUrlToRedirect")
        except ValueError as err:
            return "error getShortenedUrlToRedirect" + err.args