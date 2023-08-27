import http
import os
import subprocess

from dotenv import load_dotenv
import pytest
import requests
import retry
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError

from llama_index.llms import ChatMessage, MessageRole

SERVICE_PORT = 8080

# Arrange
@pytest.fixture(scope="session", autouse=True)
def service():
    # Setup
    load_dotenv()  # take environment variables from .env.
    os.environ['LOG_LEVEL'] = 'DEBUG'
    proc = subprocess.Popen(['uvicorn', 'app.main:app', '--port', str(SERVICE_PORT)], env=os.environ.copy())

    call_health_check()

    yield
    
    # Teardown
    proc.terminate()
    proc.wait()


@retry.retry((NewConnectionError, ConnectionError), tries=30, delay=5)
def call_health_check():
    response = requests.get(f'http://localhost:{SERVICE_PORT}/api/v1')
    assert response.status_code == http.HTTPStatus.OK, response.text


def test_call_simple_api():
    response = requests.get(f'http://localhost:{SERVICE_PORT}/api/v1/simple')
    assert response.status_code == http.HTTPStatus.OK, response.text
    assert response.json() == {"message": "Hello World"}


def test_call_ai():
    data = {
        "temperature": 0,
        "llm_engine": "openAI",
        "model": "gpt-3.5-turbo",
        "context": [{"role": "user", "content": "test"}]
    }
    response=requests.post(f'http://localhost:{SERVICE_PORT}/api/v1/chat/user_qeury',json=data)
    assert response.status_code == http.HTTPStatus.OK, response.text


def test_wrong_llm_engine():
    data = {
        "temperature": 0,
        "llm_engine": "wrongLLMengine",
        "model": "gpt-3.5-turbo",
        "context": [{"role": "user", "content": "test"}]
    }

    response=requests.post(f'http://localhost:{SERVICE_PORT}/api/v1/chat/user_qeury',json=data)
    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY, response.text

def test_one_prompt_llama():
    data = {
        "temperature": 0,
        "llm_engine": "openAI",
        "model": "gpt-3.5-turbo",
        "chat_messages": [ChatMessage(role=MessageRole.USER, 
                                      content='Why should students eat breakfast?').dict()],
        "llama_context": "infra_ui"
    }

    response=requests.post(f'http://localhost:{SERVICE_PORT}/api/v1/chat/special_assistant',json=data)
    assert response.status_code == http.HTTPStatus.OK, response.text

def test_several_prompts_llama():
    data = {
        "temperature": 0,
        "llm_engine": "openAI",
        "model": "gpt-3.5-turbo",
        "chat_messages": [ChatMessage(role=MessageRole.USER, 
                                      content='Why should students eat breakfast?').dict(), 
                          ChatMessage(role=MessageRole.ASSISTANT, content='Students should eat breakfast because it is important for their health, helps them perform well in their classes, and can help prevent diseases.').dict(),
                          ChatMessage(role=MessageRole.USER, 
                                      content='Tell me more about it').dict()],
        "llama_context": "infra_ui"
    }

    response=requests.post(f'http://localhost:{SERVICE_PORT}/api/v1/chat/special_assistant',json=data)
    assert response.status_code == http.HTTPStatus.OK, response.text
