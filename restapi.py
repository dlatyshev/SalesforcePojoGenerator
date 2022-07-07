import requests


class ApiClient:

    def __init__(self, username, password, client_id, client_secret):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.instance_url = None
        self.authorize()

    def authorize(self):
        query_params = {
            "grant_type": "password",
            "client_id": f"{self.client_id}",
            "client_secret": f"{self.client_secret}",
            "username": f"{self.username}",
            "password": f"{self.password}"
        }
        response = requests.post("https://test.salesforce.com/services/oauth2/token", params=query_params)

        self.access_token = response.json()["access_token"]
        self.instance_url = response.json()["instance_url"]

    def get_sobjects(self):
        response = requests.get(f"{self.instance_url}/services/data/v54.0/sobjects",
                                headers={"Authorization": f"Bearer {self.access_token}"})
        return response.json()["sobjects"]

    def get_sobject_description(self, sobject_name: str) -> dict:
        return requests.get(f"{self.instance_url}/services/data/v54.0/sobjects/{sobject_name}/describe",
                            headers={"Authorization": f"Bearer {self.access_token}"}).json()
