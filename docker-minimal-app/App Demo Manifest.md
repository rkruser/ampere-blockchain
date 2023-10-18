App Demo Manifest
(See hand notebook for tech stack and more details)

security and database interface library:
    /database.py
    /security.py
    /etc.

frontend server:
    /User accounts, API activation, etc.

Identity/Key server (use Authorization Bearer tokens):
    /Get the identities of all nodes, keep up to date on active ones
    /Get public keys, etc. (maybe signatures later)

API server (use Authorization Bearer tokens):
    /Allow nodes to query our API

Dev server (whitelisted admin accounts):
    /Only for admins
    /View running nodes, blockchain state, etc.

MongoDB server/volume:
    /Premade, mostly
    /Used by all other servers, at the moment

Node server:
    /For now, spawn many nodes and imitate their behavior (mockup functionality)

Redis server for caching:
    /Maybe