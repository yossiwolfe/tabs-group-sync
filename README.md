# Tab Groups Project

Syncing tab groups across multiple devices in real time

# Design Decisions

1) Using UUIDs for the Tab Group id and Tab id fields. The benefit is mathematically random ids that are extremely unlikely to collide with each other. The tradeoff is slower indexing and high storage footprint.

2) Not allowing the client to set the Tab Group id and Tab id fields manually. Both fields are generated automatically on creation. This prevents the user from setting the same id for two tab groups or tabs. The tradeoff is that for offline sync the ids may mismatch between the temporary local ones and the real ones created when the device syncs after going back online. This can be mitigated by fixing the offline ids after the sync.

3) Device id is string. This allows the client to decide what device id represents. The upside is that no JOINs are necessary and its fast to get the device id (it comes with each row) but the downside is that it increases bloat... each row needs to store the device id string instead of a relationship to a tables of device ids.