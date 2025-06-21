# RAG_server

## Quick Start

1. **Copy and configure environment variables:**
   ```sh
   cp .env.example .env
   # Edit .env as needed
   ```

2. **Build and start all services with Docker Compose:**
   ```sh
   docker-compose up --build
   ```

3. **Set up Lambda (LocalStack):**
   ```sh
   python scripts/setup_localstack.py
   ```

4. **Deploy Lambda function:**
   ```sh
   python scripts/deploy_lambda.py
   ```

## Healthchecks
- Each service in `docker-compose.yml` has a healthcheck that pings its main HTTP endpoint for better orchestration.

## .env.example
- See `.env.example` for required environment variables.

---

For more details, see the code and comments in each service directory. 