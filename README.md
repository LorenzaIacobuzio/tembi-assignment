# Tembi assignment

## Overview
This repo implements a small data pipeline that scrapes products from the e-commerce website 
Brdr Simonsen: it adds to cart a random item from a random product collection, 
retrieves the shipping provider data at checkout, normalizes the data and stores it in MySQL via SQLAlchemy. 
It runs reproducibly in Docker and includes a small REST API to inspect stored data.

## Features
- Scraper uses Playwright to navigate site and perform add-to-cart flow
- Extraction uses regex for price parsing
- Data stored in MySQL using SQLAlchemy ORM
- Docker + docker-compose to run DB, scraper, and API
- Simple CI workflow with GitHub Actions and a few tests
- README and a short design note (`design-note.md`)

## How to run
1. Copy `.env.example` to `.env` and adjust
2. Build and run:
   ```bash
   docker compose up --build
3. To run tests:
   ```python -m pytest src/tests/test_scraper.py```
4. To lint and format:
    ```python -m black .```
    ```python -m flake8 .```
5. To see results, open browser at
    ```http://localhost:8000/products```