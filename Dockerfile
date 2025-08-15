FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . /usr/src/app
ENV PROJECT_ROOT /usr/src/app
#ENV LIVE_TESTS 0
#RUN ./scripts/tests.sh
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]
