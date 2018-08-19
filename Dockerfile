FROM python:3-alpine

RUN apk update \
        && apk add --no-cache git openssh-client \
        && pip install pipenv \
        && addgroup -S -g 1001 app \
        && adduser -S -D -h /app -u 1001 -G app app

# Creating working directory
RUN mkdir /app/src
WORKDIR /app/src
RUN chown -R app.app /app/

# Install requirements
RUN pipenv install

# Expose webhook port
EXPOSE 443

# Creating environment
USER app
COPY . /app/src

CMD [ "pipenv", "run", "python", "main.py" ]
