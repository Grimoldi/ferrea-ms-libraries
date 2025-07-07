# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.8
FROM python:${PYTHON_VERSION}-slim AS base

# Prevent Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout and sderr
ENV PYTHONUNBEFFERED 1

# set the working directory
WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install git for external dependencies
RUN apt-get -y update
RUN apt-get -y install git

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# copy the scripts to the folder
COPY ./src .

# start the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
