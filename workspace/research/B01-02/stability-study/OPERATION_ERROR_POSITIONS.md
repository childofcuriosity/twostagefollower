# Where do operation errors occur when correct names are supplied?
This is a diagnostic test, not unassisted actual execution. Operations can be wrong even with correct names. Current state always follows actual generation and is not corrected by the program.
Previously all correct counts only examples reaching a position with no earlier operation errors, separating newly occurring errors from behavior after an error. This is not randomized grouping and does not support causal claims.

|Model|Training|Tool position|Reached|Operations correct among reached|Previously all correct|Current correct given previously all correct|
|---|---|---:|---:|---:|---:|---:|
|qwen32b|Joint training|1|288|288|288|288|
|qwen32b|Joint training|2|288|288|288|288|
|qwen32b|Joint training|3|288|274|288|274|
|qwen32b|Joint training|4|288|274|274|264|
|qwen32b|Joint training|5|288|263|264|254|
|qwen32b|Joint training|6|288|256|254|234|
|qwen32b|Joint training|7|287|256|234|218|
|qwen32b|Joint training|8|283|233|218|196|
|qwen32b|Operation-only training|1|288|288|288|288|
|qwen32b|Operation-only training|2|288|288|288|288|
|qwen32b|Operation-only training|3|288|288|288|288|
|qwen32b|Operation-only training|4|288|287|288|287|
|qwen32b|Operation-only training|5|288|284|287|283|
|qwen32b|Operation-only training|6|288|283|283|279|
|qwen32b|Operation-only training|7|288|282|279|273|
|qwen32b|Operation-only training|8|288|276|273|261|
|qwen3b|Joint training|1|288|284|288|284|
|qwen3b|Joint training|2|288|288|284|284|
|qwen3b|Joint training|3|288|256|284|256|
|qwen3b|Joint training|4|288|241|256|220|
|qwen3b|Joint training|5|288|228|220|183|
|qwen3b|Joint training|6|288|243|183|168|
|qwen3b|Joint training|7|286|182|168|128|
|qwen3b|Joint training|8|285|229|128|102|
|qwen3b|Operation-only training|1|288|288|288|288|
|qwen3b|Operation-only training|2|288|276|288|276|
|qwen3b|Operation-only training|3|288|264|276|256|
|qwen3b|Operation-only training|4|288|237|256|213|
|qwen3b|Operation-only training|5|288|260|213|199|
|qwen3b|Operation-only training|6|288|249|199|180|
|qwen3b|Operation-only training|7|288|242|180|160|
|qwen3b|Operation-only training|8|288|218|160|130|
