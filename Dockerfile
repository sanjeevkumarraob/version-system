FROM python:3.12-rc-bullseye

WORKDIR /usr/src/version_system

ENV PREFIX=

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod 755 /usr/src/version_system/entrypoint.sh \
    && chmod -R 755 /usr/src/version_system/ \
    && chmod 755 /usr/src/version_system/version.sh \
    && chmod 755 /usr/src/version_system/get-version.py

ENTRYPOINT [ "/usr/src/version_system/entrypoint.sh" ]