#import "../data.typ": *

*Synthetic data.* SynthPAI comments are generated, not written by real people. Its authors report that conclusions carry over to real data @yukhymenko2024synthpai, but real users may give fewer or different clues.

*Sample size.* We evaluate #S.n_profiles authors, and each attribute is scored only for authors where a human marked it inferable, so some cells rest on a few dozen authors. The confidence intervals in @fig:acc are wide accordingly.

*One vendor, two models.* Both models are Gemini Flash-Lite models from one provider. Other free models, or larger paid ones, may be stronger or weaker; ours is a lower bound on what a determined adversary can do for free. A planned third model (Gemini 3.5 Flash) was dropped because free-tier rate limits made it too slow to complete.

*Quota limits.* The free tier refused #S.n_errors of #S.n_predictions inference requests and some judge calls. We exclude these rather than count them as wrong, which assumes the refusals are unrelated to how revealing the text is (quota refusals depend on request timing, not content).

*Free models change.* Free-tier models are updated and withdrawn without notice. We release every raw request and response so the results can be checked even if the models disappear.

*LLM judge and self-rating.* Free-text attributes are scored by an LLM judge, and meaning preservation is rated by the same model that did the rewriting, which may be lenient toward its own output. The judge was not validated against human ratings in this study; its decisions are released for inspection.

*One rewrite prompt.* We test a single, simple rewrite prompt. Stronger, iterative anonymizers @staab2025anonymizers would likely do better; our result shows what a minimal step achieves, not the limit of defenses.

*Network adversary not measured.* The network columns of @tab:net come from the threat model and prior work, not from our own measurement.
