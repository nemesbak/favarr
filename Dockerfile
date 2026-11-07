FROM python:3.12-alpine
WORKDIR /app
COPY favarr.py aviso.mkv portada.jpg ./
ENV PYTHONUNBUFFERED=1 TZ=Europe/Madrid
RUN apk add --no-cache tzdata
CMD ["python", "favarr.py"]
