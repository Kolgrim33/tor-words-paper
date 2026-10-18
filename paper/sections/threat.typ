We consider a user who posts short public comments (for example on a forum) while connected through Tor or a VPN. The user's goal is to stay unlinkable to their real-world identity.

The *network adversary* observes connections to the forum. Without an anonymity tool, the source IP address can be geolocated, which usually reveals the country and sometimes the city, though city-level geolocation databases are often wrong @poese2011geolocation. It reveals nothing about age, sex, education, occupation, income or relationship status. With Tor or a VPN, the adversary sees only the exit relay's address, which reveals nothing about the user.

The *text adversary* has no network access at all. It collects the user's public comments (by username) and sends them to an LLM with a prompt asking for a best guess of eight personal attributes. It needs no technical skill, no training data and, as we show, no money. Its output is a structured profile that could be combined with other sources to narrow down or re-identify the user.

Anonymity tools defeat the first adversary completely and the second not at all. The question is how much the second one learns.
