FROM python:3.12-alpine
WORKDIR /app
COPY pidelo.py aviso.mkv ./
ENV PYTHONUNBUFFERED=1 TZ=Europe/Madrid
RUN apk add --no-cache tzdata
CMD ["python", "pidelo.py"]
