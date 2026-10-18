#import "../data.typ": *

@tab:acc gives inference accuracy for every attribute, model and condition, and @fig:acc shows the same numbers with their 95% confidence intervals. Of the #S.n_predictions inference requests, #S.n_errors were refused by free-tier quota limits and are excluded; judge calls refused the same way are also excluded, which is why the number of scored authors differs slightly between cells.

#figure(
  {
    set text(8.5pt)
    let cols = (auto, auto) + S.models.map(_ => (auto, auto)).flatten()
    table(
      columns: cols,
      align: (left,) + (right,) * (cols.len() - 1),
      stroke: none,
      table.hline(),
      table.header(
        [*Attribute*], [*n*],
        ..S.models.map(m => table.cell(colspan: 2, align: center)[*#raw(short(m))*]),
      ),
      [], [], ..S.models.map(_ => ([orig.], [rewr.])).flatten(),
      table.hline(stroke: 0.4pt),
      ..ATTRS.map(a => {
        let first = acc_of(a, S.models.at(0), "original")
        (label(a), first.n) + S.models.map(m => (
          pct(acc_of(a, m, "original").acc),
          pct(acc_of(a, m, "rewritten").acc),
        )).flatten()
      }).flatten(),
      table.hline(),
    )
  },
  caption: [Attribute-inference accuracy on original and rewritten comments. _n_ is the number of scored authors for the first model on original text (authors for whom a human marked the attribute as inferable, minus refused requests); per-cell counts are in the released CSV.],
) <tab:acc>

#figure(
  image("/results/fig_accuracy.png", width: 100%),
  caption: [Accuracy per attribute with 95% bootstrap confidence intervals, before (left) and after (right) the rewrite defense.],
) <fig:acc>

*Network versus text.* @tab:net puts the two adversaries side by side. Without an anonymity tool, the network adversary learns the country and, unreliably, the city from the IP address; with Tor it learns nothing. The text adversary, which is unaffected by Tor, recovers every attribute well above zero. Averaged over the attributes, the best free model is right #pct(mean_best("best_original")) of the time on the original comments.

#figure(
  {
    set text(8.5pt)
    table(
      columns: (auto, 1fr, auto, auto, auto),
      align: (left, left, left, right, right),
      stroke: none,
      table.hline(),
      table.header([*Attribute*], [*IP, no Tor*], [*IP, Tor*], [*Text*], [*Text, rewritten*]),
      table.hline(stroke: 0.4pt),
      ..NET.map(r => (label(r.attr), r.network_no_tor, r.network_tor, pct(r.best_text_acc), pct(r.best_text_acc_rewritten))).flatten(),
      table.hline(),
    )
  },
  caption: [What each adversary learns. Network columns are analytical (from the threat model, @poese2011geolocation); text columns are the best measured model accuracy.],
) <tab:net>

*Rewrite defense.* The single-pass rewrite lowers the best model's mean accuracy from #pct(mean_best("best_original")) to #pct(mean_best("best_rewritten")), but no attribute falls to zero. The rewriter rated its own rewrites at #calc.round(S.mean_meaning, digits: 2) out of 5 for meaning preservation on average (#S.n_meaning authors).

