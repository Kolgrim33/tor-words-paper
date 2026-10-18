// Shared data and helpers. Every number in the paper is read from /results.
#let S = json("/results/summary.json")
#let META = json("/results/run_meta.json")
#let ACC = csv("/results/table_accuracy.csv", row-type: dictionary)
#let pct(x) = str(calc.round(float(x) * 100, digits: 1)) + "%"
#let short(m) = m.split("/").last()
#let label(a) = (
  "age": "Age (±5 y)", "sex": "Sex", "city_country": "City", "country": "Country",
  "birth_city_country": "Birthplace", "education": "Education", "occupation": "Occupation",
  "income_level": "Income level", "relationship_status": "Relationship",
).at(a, default: a)

#let NET = csv("/results/table_network_vs_text.csv", row-type: dictionary)
#let ATTRS = NET.map(r => r.attr)
#let acc_of(attr, model, cond) = ACC.find(r => r.attr == attr and r.model == model and r.condition == cond)
// Mean over attributes of the best model's accuracy in one condition.
#let mean_best(key) = {
  let xs = ATTRS.map(a => float(S.at(key).at(a).acc))
  xs.sum() / xs.len()
}
