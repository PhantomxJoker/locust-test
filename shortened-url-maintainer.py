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
    host = os.environ.get('api-host')
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

    def deleteFromFile(self, filename, instance = "shortened-urls"):
        try:
            files = os.listdir(self.path_base + instance)
            if len(files) > 0 and exists(self.path_base + instance + "/" + filename + ".txt"):
                os.remove(self.path_base + instance + "/" + filename + ".txt")
        except ValueError as err:
            return "error deleteFromFile" + err.args

    @task(1)
    def removeShortenedUrl(self):
        shortened_info = self.randomFromFile("shortened-urls")
        if shortened_info != 0:
            headers = { "Content-Type": "application/json" }
            shortened_array = str(shortened_info).split(";")
            shortened_id = shortened_array[2]

            rs = self.client.delete("/shortened_urls/{0}".format(shortened_id),
            headers=headers,
            name="/removeShortenedUrl")
            if rs.status_code == 200:
                self.deleteFromFile(shortened_id, "shortened-urls")

    @task(1)
    def editShortenedUrl(self):
        shortened_info = self.randomFromFile("shortened-urls")
        if shortened_info != 0:
            headers = { "Content-Type": "application/json" }
            shortened_array = str(shortened_info).split(";")
            shortened_id = shortened_array[2]

            rs = self.client.patch("/shortened_urls/{0}".format(shortened_id), json = {
                "url": "https://www.google.com",
                "name": "Edited",
                "enabled": True
            },
            headers=headers,
            name="/editShortenedUrl")

    @task(2)
    def getPaginatedShortenedUrls(self):
        headers = { "Content-Type": "application/json" }

        rs = self.client.get("/shortened-urls?page=1&limit=10",
        headers=headers,
        name="/getPaginatedShortenedUrls")

    @task(3)
    def getShortenedUrlById(self):
        shortened_info = self.randomFromFile("shortened-urls")
        if shortened_info != 0:
            headers = { "Content-Type": "application/json" }
            shortened_array = str(shortened_info).split(";")
            shortened_id = shortened_array[2]

            rs = self.client.get("/shortened_urls/{0}".format(shortened_id),
            headers=headers,
            name="/getShortenedUrlById")

    @task(5)
    def createShortenedUrl(self):
        headers = { "Content-Type": "application/json" }

        item_url = "https://www.mercadolibre.cl/"
        item_name = "Meli"

        rs = self.client.post("/shortened-urls", json = {
            "url": item_url,
            "name": item_name,
            "enabled": True
        }, headers = headers, name = "/createShortenedUrl")
        response_json = rs.json()
        shortened_info = item_name + ";" + item_url + ";" + response_json['shortened']
        if rs.status_code == 201:
            with open(self.shortened_url_path + response_json['shortened'] + ".txt", "w", newline='') as f:
                f.write(shortened_info)
                f.close()