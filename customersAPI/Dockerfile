FROM python:3.12-slim

# Instala solo el componente gcloud necesario
RUN apt-get update && apt-get install -y \
    curl \
    && curl -sSL https://sdk.cloud.google.com > /tmp/install.sh \
    && bash /tmp/install.sh --disable-prompts --install-dir=/usr/local \
    && apt-get remove -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/install.sh

ENV PATH $PATH:/usr/local/google-cloud-sdk/bin

WORKDIR /app

COPY wait_for_spanner.sh /usr/bin/wait_for_spanner
RUN chmod +x /usr/bin/wait_for_spanner

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["wait_for_spanner", "uvicorn", "customersAPI.api:app", "--host", "0.0.0.0", "--port", "8001"]