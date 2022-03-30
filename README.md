# Rand Engine Project

This projects has the goal to provide random data to supply Data Engineering Learning




It has to sub modules, batch and streaming. That bring us to the fact that in batch operations it's possible to create vectorized ways to construct columns, being faster. The random data generation here has the paradigm of receive metadata for columns and so generate a dataframe or a table with ht passed number of rows.

On the other hand, streaming data must be based on the line paradigm, and as a line or a message has many files and each of them has a type, it's a little bit slower, creating a line (message) almost continuously. 


PS: Sorry about my english below. I will improve this README.md file as soon as possible.


# Rand Engine Batch


# Rand Engine Streaming