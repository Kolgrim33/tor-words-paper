#import "data.typ": *

#set document(title: "Tor Hides Your IP, Not Your Words", author: "Selby Mashiki")
#set page(paper: "a4", margin: (x: 2.2cm, y: 2.4cm), numbering: "1")
#set text(font: "New Computer Modern", size: 10.5pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")
#show heading: set block(above: 1.3em, below: 0.7em)

#align(center)[
  #text(17pt, weight: "bold")[Tor Hides Your IP, Not Your Words:\ Free LLMs as an Attribute-Inference Threat to Users of Network Anonymity Tools]
  #v(0.6em)
  #text(11pt)[Selby Mashiki] \
  #text(9.5pt)[Information Management and Technology, National University of Science and Technology (NUST), Zimbabwe] \
  #text(9.5pt)[Preprint, #META.date]
]

#v(0.8em)
#block(inset: (x: 1.2cm))[
  *Abstract.* #include "sections/abstract.typ"
]

= Introduction
#include "sections/intro.typ"

= Threat Model
#include "sections/threat.typ"

= Related Work
#include "sections/related.typ"

= Method
#include "sections/method.typ"

= Results
#include "sections/results.typ"

= Discussion
#include "sections/discussion.typ"

= Limitations
#include "sections/limitations.typ"

= Ethics
#include "sections/ethics.typ"

= Conclusion
#include "sections/conclusion.typ"

#bibliography("refs.yml", style: "ieee")
