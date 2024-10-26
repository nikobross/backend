Name: Niko Ross
NetID: nb26

Challenges Attempted: Tier (I/II/III) All

Why it is important that these routes require authorization?

Authorization is necessary for getting a user and sending money because without it anyone who knows about
the URL that accesses the route could gain access to the account of anyone and make edits or send money.

Why hashing is important?

Without hashing passwords, they are stored in plaintext, making them 
accessible to anyone who gains unauthorized access to the database. Hashing them
reduces the chance of data breaches.

What are rainbow tables and how do they work?

Rainbow tables are a tool for decrypting hashed passwords built from a precomputed hashing algorithm.
With a single-hashed password you can look up the password in a rainbow table and find the plain text
password.


What is password salting and how can it protect against rainbow tables?

Password salting is the practive of adding a value to each password 
before hashing to ensure that identical passwords have different hashes. 
This helps protect against rainbow tables.

What is iterative hashing and how can it protect against rainbow tables?

Iterative hashing is where a password is hashed many times in a row. This makes it
impossible to search up a pasword in a rainbow table becuase you don't know how many times
a password has been hashed.