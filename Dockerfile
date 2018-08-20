FROM python:3.7

# Creating working directory
RUN mkdir -p /app/src
WORKDIR /app/src

RUN pip install pipenv

# Expose webhook port
EXPOSE 443

# Creating environment
COPY . /app/src
RUN pipenv install

CMD [ "pipenv", "run", "python", "main.py" ]
