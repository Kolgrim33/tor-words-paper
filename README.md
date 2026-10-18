# Tor Hides Your IP, Not Your Words

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23453955.svg)](https://doi.org/10.5281/zenodo.23453955)

Code, data pipeline and raw results for the preprint *"Tor Hides Your IP, Not Your Words: Free LLMs as an Attribute-Inference Threat to Users of Network Anonymity Tools"* by Selby Mashiki (NUST, Zimbabwe).

Network anonymity tools such as Tor and VPNs hide *where* you connect from. They do not hide *what you write*. This study measures how accurately free-tier large language models infer eight personal attributes (age, sex, location, birthplace, education, occupation, income level, relationship status) from synthetic online comments, compares that with what an IP address reveals, and tests a "rewrite before posting" defense.

## Data

[SynthPAI](https://huggingface.co/datasets/RobinSta/SynthPAI) (Yukhymenko et al., NeurIPS 2024), licensed **CC BY-NC-SA 4.0**. All profiles are synthetic. The dataset is not redistributed here; download it with:

```bash
mkdir -p data/raw
curl -L -o data/raw/synthpai.jsonl https://huggingface.co/datasets/RobinSta/SynthPAI/resolve/main/synthpai.jsonl
```

## Reproduce

Requires [uv](https://docs.astral.sh/uv/) and a free Google Gemini API key.

```bash
uv sync
uv run pytest                      # unit tests, no network
echo "GEMINI_API_KEY=..." > .env   # gitignored
uv run python -m torwords.run --models gemini/gemini-3.1-flash-lite,gemini/gemini-3.5-flash-lite,gemini/gemini-3.5-flash --n 100
uv run python -m torwords.report  # tables, figure, summary.json
uv run --with typst python -c "import typst; typst.compile('paper/main.typ', output='paper/main.pdf', root='.')"
```

Model outputs change over time, so a rerun will not match exactly. The raw outputs from the run reported in the paper are in `results/raw/` and `results/calls.jsonl.gz`, and every number in the paper is read from `results/` at build time.

## Layout

```
src/torwords/   data, llm (cached client), infer, rewrite, score, run, report
tests/          unit tests (pytest)
results/        raw predictions, rewrites, tables, figure, summary.json
paper/          Typst source and PDF
```

## License

Code: MIT. Data derived from SynthPAI: CC BY-NC-SA 4.0.

## Citation

```bibtex
@misc{mashiki2026torwords,
  title  = {Tor Hides Your IP, Not Your Words: Free LLMs as an Attribute-Inference Threat to Users of Network Anonymity Tools},
  author = {Mashiki, Selby},
  year   = {2026},
  note   = {Preprint}
}
```
