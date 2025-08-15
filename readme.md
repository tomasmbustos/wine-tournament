# Sample python backed web server

This uses
- FastAPI
- Dependency Injection
- Clean Architecture
- Test Driven Development

### Getting Started
1. Rename the `.env.example` to `.env` and update the values (specially the PROJECT_ROOT)
2. Create a new virtual environment (check the Dockerfile for the python version to use)
3. Install the dependencies with `pip install -r requirements.txt`
4. Run with `python main.py`
5. Open the browser and go to `http://0.0.0.0:8888/docs` to see the API documentation