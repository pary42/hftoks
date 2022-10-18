# hftoks
High Frequency Tokens


## Usage

`hftoks` depends on pretokenization with the `pretokenize` script.

First run `pretokenize`:

    pretokenize < PLAIN_TEXT_FILE > PRETOK_TEXT_FILE

Then you can learn the vocabulary from pretokenized text. `VOCAB_SIZE`
is the (minimal) number of produced subword tokens (defaults to
3000). `STEP_SIZE` is the number of subwords added to the vocabulary in
each iteration (defaults to 5% of `VOCAB_SIZE`).

    hftoks.py learn PRETOK_TEXT_FILE OUT_VOCAB_FILE [VOCAB_SIZE [STEP_SIZE]]

Then you can tokenize the pretokenized text:

    hftoks.py tokenize VOCAB_FILE < PRETOK_TEXT_FILE > OUT_TOKENS
    cat PLAIN_TEXT | pretokenize | hftoks.py tokenize VOCAB_FILE > TOKENS

Use `detokenize` to get plain text from tokens:

    detokenize < TOKENS > PLAIN_TEXT_FILE

