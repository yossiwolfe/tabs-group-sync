# Tab Groups Project

Syncing tab groups across multiple devices in real time

# Design Decisions

1) Using UUIDs for the Tab Group id and Tab id fields. The benefit is mathematically random ids that are extremely unlikely to collide with each other.

2) Not allowing the client to set the Tab Group id and Tab id fields manually. Both fields are generated automatically on creation. This prevents the user from setting the same id for two tab groups or tabs.

3) Device id is string. This allows the client to decide what device id represents.