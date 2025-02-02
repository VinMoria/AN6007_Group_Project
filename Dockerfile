FROM python
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-t","5", "-b", "0.0.0.0:8000", "app:app"]