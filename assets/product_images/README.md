# Product Image Placeholders

These PNG files act as default shoe photos for the Retailer AI Agent prototype. The database seeder uploads each file to LocalStack S3 and stores the resulting URL on every product record. Name assets after the product SKU (e.g., `run-001.png`) to bind an image to that specific product; any other filename is treated as a generic fallback. Add or replace files in this folder if you want new imagery—any PNG/JPG/WebP/SVG asset will be picked up the next time you run `task db:seed`.
