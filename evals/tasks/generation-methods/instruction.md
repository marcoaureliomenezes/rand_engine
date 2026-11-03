Use the Python library `rand-engine` (already installed) to generate the popularity of 5,000 products: `product_views.csv` in the current directory, with columns `product_id` (1 to 5,000, sequential) and `views` (a positive integer per product). Views must follow a Zipf-like power law with exponent 1.5: a few products get huge counts, most get very few.

Save the generating script as `solve.py` in the current directory, with a fixed seed, so that re-running it rebuilds the same file.
