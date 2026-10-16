Temperature = how adventurous the probability distribution is.
Top-k = how many candidates are allowed.
Top-p = how much cumulative probability is allowed

But mathematically, thinking of top-p as sorting all candidate tokens by probability and accumulating them is exactly right.

One small implementation detail: real inference engines don't necessarily perform a slow, naive Python-style sort of the entire vocabulary every time. GPU kernels and optimized sampling algorithms can make this much faster.
128,000 tokens

↓ 
discard almost everything tiny

500 plausible tokens

↓ 
order / process these

top-p cutoff




##### Navigable small world is used to retrieve information

It trades precision for speed