FROM python:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

#CMD [ "python3", "-m" , "streamlit", "run", "mosipgenaiserver.py", "--server.address=0.0.0.0",  "--server.port=5000"]
CMD [ "python3", "mosipgenaiserver.py", "--server.address=0.0.0.0", "--server.port=5000"]

