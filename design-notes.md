# Design notes

## Considerations and improvement
- **XPath**: Not used due to time constraints
- **Deduplication & validation**: Deduplication of shipping providers is done via name matching. In production, a shipping provider would be associated with IDs instead of names
- **Tests**: Adding a `docker-compose.yml` for tests would allow to have db test container to populate with test data and be able to test full flow and persistence behaviour through integration tests. Unit tests and edge cases should also be extensively present
- **Secrets**: In production, env variables would be injected as secrets and might be injected from an orchestrator
- **Monitoring**: Add alerting on scraping errors, high failure rates, or database connectivity issues
- **Observability**: Add structured logging (JSON), metrics (Prometheus) and traces (OpenTelemetry) for latency & error monitoring
- **Parallel scraping**: The current script scrapes sequentially. In production, a scraper orchestrator service could queue a message to Kafka for each site to be scraped, which would be consumed by a dedicated scraper service (one service per website)
- **Resilience**: Wrap network-dependent steps (page navigation, click events, JSON fetch) in retry loops with exponential backoff and random delays to avoid IP blocking. Use capture of page screenshot on failure to aid debugging. Maybe save partially populated data and refill at later stage
- **Transactions**: Right now rows are committed to different tables in separate commits, this is very bad practice. Wrap db inserts into one transaction to guarantee data integrity
- **Inserts**: Upserts/getOrCreate to avoid duplication of existing products
- **Constraints**: Enforce unique key constraints on product URL to avoid duplication, avoid using rolling IDs and use UUID for product uniqueness across db partitions/sharding
- **ETL**: Have a slim scraper service (easy to scale) that extracts data into intermediate tables, and have serverless functions to periodically clean, normalize and enrich data
- **Caching**: Caching a product URL avoids fetching collections and products everytime just to select a random one (if shipping providers is the end goal, and not product scraping per se)
- **Orchestrators**: AWS and Kubernetes orchestrators can scale pods automatically based on traffic, and so do Kafka topics
- **Partitions**: Cache partition can be done by region if market insights based on country are needed
- **Batch processing**: When scrapers scale, inserts can overload db. If scrapers write to queue (Kafka), then a batching service collects messages and performs batch inserts on db
- **Workflows**: Add GH workflow for Dockerizing app and pushing to registry

## Personal consideration
I have worked on this much more than 2-3h, because the constraints were strict, 
I had never used Python for server-side applications, and the website operations were completely 
unknown to me. 
As a result, the scraping is not always reliable: sometimes it times out, sometimes the price is 0,
or no shipping providers are found.
I am still satisfied considering the time/techstack constraints and my lack of scraping experience.
