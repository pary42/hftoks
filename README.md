# hftoks
High Frequency Tokens


## Usage

`hftoks` depends on pretokenization with the `pretokenize` script.

First run `pretokenize`:

    pretokneize < PLAIN_TEXT_FILE > PRETOK_TEXT_FILE

Then you can lear the vocabulary from pretokenized text. `VOCAB_SIZE`
is the (minimal) number of produced subword tokens (defaults to
3000). `STEP_SIZE` is number of subwords added to the vocabulary in
each iteration (defautls to 5% of `VACAB_SIZE`).

    hftoks.py learn PRETOK_TEXT_FILE OUT_VOCAB_FILE [VOCAB_SIZE [STEP_SIZE]]

The you can tokenize pretokenized text:

    hftoks.py tokenize VOCAB_FILE < PRETOK_TEXT_FILE > OUT_TOKENS
    cat PLAIN_TEXT | pretokneize | hftoks.py tokenize VOCAB_FILE > TOKENS

Use `detokneize` to get plain text from tokes:

    detokneize < TOKENS > PLAIN_TEXT_FILE

