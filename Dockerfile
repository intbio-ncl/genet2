# syntax=docker/dockerfile:1
FROM python:3.10
WORKDIR /python-docker
COPY . /python-docker/
RUN pip install -r requirements.txt
ENV FLASK_APP=router.py
RUN python -m spacy download en_core_web_sm
RUN python -m pip install python-Levenshtein
CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0"]

