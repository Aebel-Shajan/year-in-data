FROM python:3.10

WORKDIR /app
COPY ./ /app/
RUN chmod +x scripts/run-pipeline.sh
CMD ["./scripts/run-pipeline.sh"]