Network anonymity tools such as Tor @dingledine2004tor and VPNs are often described as making their users "anonymous". What they actually protect is the _channel_: they hide which IP address is talking to which server, so a website, an internet provider or an eavesdropper cannot tie traffic to a person's network location. They do nothing to the _content_ a user chooses to publish. A comment posted over Tor is just as revealing as the same comment posted from a home connection.

From an information-management point of view, every public post is a record. It persists, it can be collected in bulk, and it carries metadata about its author that the author never meant to disclose: hints about where they live, how old they are, what they do for a living. Contextual-integrity theory @nissenbaum2004contextual frames the harm well: information shared for one purpose (a casual comment about local food) flows into another (a profile of the author) without the author's consent.

Until recently, turning such scattered hints into a profile required a skilled human investigator, which limited the threat to targeted cases. Staab et al. @staab2024beyond showed that large language models (LLMs) can do this automatically and at scale, with GPT-4 inferring personal attributes from Reddit comments with accuracy close to human investigators at a fraction of the cost and time. Their follow-up dataset, SynthPAI @yukhymenko2024synthpai, made it possible to study this threat on synthetic, privacy-safe data.

This paper asks what that finding means for the users of anonymity tools specifically, and whether the threat is now available to anyone at no cost. We make three contributions:

+ *Network versus text.* We contrast what a network observer learns from a user's IP address with what an LLM learns from the same user's text, attribute by attribute, and show that removing the IP leaves most of the profile intact.
+ *Zero-cost adversary.* We measure attribute inference using only free-tier models (Google Gemini Flash-class models on the free API tier), showing that the attack no longer requires a paid frontier model.
+ *A simple defense, measured.* We test a "rewrite before posting" step, in which an LLM paraphrases comments to strip personal clues, and measure how much it reduces inference accuracy and how much meaning it keeps.

The code and all raw model outputs are released so that every number in this paper can be recomputed.
