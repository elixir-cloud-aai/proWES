from logging import Logger
import socket

import requests
from requests import Session
import urllib3

class wesClient:
    def __init__(self,url:str, base_path:str, token: Optional[str] = None,)-> None:
        """Class Constructor"""
        self.url = url
        self.base_path = base_path
        self.headers = {"Accept": "application/json"}
        self.session = Session()
        self.session.headers.update(self.headers)  
        self.token = token
        
    def get_runs(self,token:Optional[str] = None):
        url = f"{self.url}{self.base_path}/runs"
        response = self.session.get(url)
        if token:
            self.token = token
            self.headers
        try:
            response = self.session.get(url)
            data = response.json()
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        return data
    
    def get_runs_id(self,run_id:str,token:Optional[str] = None):
        url =f"{self.url}{self.base_path}/runs/{run_id}"
        if token:
            self.token = token
            self.headers
        try:
            response = self.session.get(url)
            data = response.json()
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        return data
    def get_service_info(self,token:Optional[str] = None):
        url =f"{self.url}{self.base_path}/service-info"
        if token:
            self.token = token
            self.headers
        try:
            response = self.session.get(url)
            data = response.json()
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        return data
    def get_run_id_status(self,run_id:str,token:Optional[str] = None):
        url =f"{self.url}{self.base_path}/runs/{run_id}/status"
        if token:
                self.token = token
                self.headers
        try:
            response = self.session.get(url)
            data = response.json()
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        return data
        
    def post_workflow(self,input_data,token:Optional[str]=None):
        input_data= input_data
        url = f"{self.url}{self.base_path}/runs"
        if token:
                self.token = token
                self.headers
        try:
            response  = self.session.post(url,json=input_data)
            data = response.json()
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        return data





    
# # For Testing the above client methods
# url = "https://wes.rahtiapp.fi"
# base_path = "/ga4gh/wes/v1"
# c = wesClient(url, base_path)
# c.get_runs()
# c.get_runs_id("N5H4TT")
# c.get_service_info()
# c.get_run_id_status("N5H4TT")
# c.post_workflow("")