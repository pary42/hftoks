#!/usr/bin/python3


import sys
#from trie import Trie
from heapq import nlargest


class Trie:
    def __init__(self, freq=0, ID=None):
        self.sub = {}
        self.freq = freq
        self.ID = ID

    def __str__(self):
        return '<Trie: freq=%d, ID=%s, sub=%s>' \
            % (self.freq, self.ID, list(self.sub.keys()))

    def is_final(self):
        return self.ID is not None

    def forward(self, byte):
        return self.sub.get(byte)

    def incr_node(self, delta):
        if self.ID is None:
            self.ID = 0
        self.freq += delta

    def findr(self, sequence):
        if len(sequence) == 0:
            if self.ID is None:
                return None
            else:
                return self
        if sequence[0] in self.sub:
            return self.sub[sequence[0]].find(sequence[1:])
        return None

    def find(self, sequence):
        this = self
        for b in sequence:
            this = this.sub.get(b)
            if this is None:
                return None
        return this

    def find_prefix(self, sequence):
        this = self
        for i,b in enumerate(sequence):
            nxt = this.sub.get(b)
            if nxt is None:
                return this, sequence[i:]
            this = nxt
        return this, []

    def get(self, sequence):
        n = self.find(sequence)
        if n is None:
            return 0, None
        return n.freq, n.ID
    
    def get_freq(self, sequence):
        n = self.find(sequence)
        if n is None or n.ID is None:
            return None
        return n.freq
    
    def setupr(self, sequence):
        if len(sequence) == 0:
            return self
        nxt = self.sub.get(sequence[0])
        if  nxt is None:
            nxt = Trie()
            self.sub[sequence[0]] = nxt
        return nxt.setupr(sequence[1:])
    
    def setup(self, sequence):
        """Creates Trie nodes representing sequence, returns the last node
        """
        assert sequence[0] not in self.sub
        this = self
        for b in sequence:
            n = Trie()
            this.sub[b] = n
            this = n
        return this

    def increment(self, sequence, delta):
        """Increment `sequence` frequency with `delta`, setup if not exists
        """
        n,s = self.find_prefix(sequence)
        if len(s) > 0:
            n = n.setup(s)
        n.incr_node(delta)

    def items_y(self, prefix=()):
        if self.is_final():
            yield (prefix, self.freq, self.ID)
        for b,n in self.sub.items():
            yield from n.items_y(prefix + (b,))

    def items(self):
        stack = [(self, ())]
        while stack:
            node, pref = stack.pop()
            if node.is_final():
                yield (pref, node.freq, node.ID)
            for b,n in node.sub.items():
                stack.append((n, pref + (b,)))


    def items_l(self):
        out = []
        self.items_append((), out)
        return out
    
    def items_append(self, prefix, out):
        if self.is_final():
            out.append((prefix, self.freq, self.ID))
        for b,n in self.sub.items():
            n.items_append(prefix + (b,), out)

### end of class Trie


            
def word_counts(iterator):
    words = Trie()
    for w in iterator:
        words.increment(w, 1)
    return words

def read_vocab(filename):
    voc = Trie()
    for line in open(filename, encoding='utf-8'):
        w, f = line[:-1].split('\t')
        voc.increment(w, int(f))
    return voc

def vocab_from_bytes(allwords):
    vocab = Trie()
    candid = Trie()
    for w,f,_ in allwords.items():
        b0 = w[0]
        vocab.increment((b0,), f)
        for b1 in w[1:]:
            vocab.increment((b1,), f)
            candid.increment((b0, b1), f)
    return vocab, candid

def vocab_from_segments(allwords, vocab):
    nextvocab = Trie()
    candid = Trie()
    for w,f,_ in allwords.items():
        segs = best_toks(w, vocab)
        s1 = segs[0]
        nextvocab.increment(s1, f)
        for s2 in segs[1:]:
            nextvocab.increment(s2, f)
            candid.increment(s1 + s2, f)
            s1 = s2
    return nextvocab, candid

class SegScore:
    # starting and eding position of the best segment ending here
    beg = -1
    end = -1
    # number of segments of the best segmentation ending here
    cnt = 1000
    # ??? sum of frequences of the best segmentation
    sum = 0

    def __init__(self, start = None):
        if start is None:
            return

    def is_better(self, that):
        # highest priority: minimum number of segments
        if self.cnt < that.cnt:
            return True
        if self.cnt > that.cnt:
            return False
        # next priority: maximum sum of segments' frequencies
        #print('is_better:', self.sum, that.sum, self.end, that.end, self.beg, that.beg)
        return self.sum > that.sum

    def next(self, thispos, thisfreq):
        s = SegScore()
        s.beg = self.end
        s.end = thispos
        s.cnt = self.cnt + 1
        #s.sum = self.sum + thisfreq
        s.sum = min(self.sum, thisfreq)
        return s
        

def best_toks(word, vocab):
    scores = [SegScore() for _ in range(len(word)+1)]
    scores[0].end = 0
    scores[0].cnt = 0
    for start in range(len(word)):
        t = vocab
        startseg = scores[start]
        for i in range(start, len(word)):
            t = t.forward(word[i])
            if t is None:
                break
            if t.is_final():
                # possible segment end
                this = startseg.next(i+1, t.freq)
                if this.is_better(scores[i+1]):
                    scores[i+1] = this
                    #print(i, this.beg, this.end)

    segments = []
    i = len(word)
    while i > 0:
        s = scores[i]
        segments.append(word[s.beg:s.end])
        i = s.beg
    segments.reverse()
    return segments

def process_text(word_iter, vocab_size=2000, step_size=100):
    allwords = word_counts(word_iter)
        
    # Frist phase, working with individual bytes
    vocab, candidates = vocab_from_bytes(allwords)
    singles = set(b for b,_,_ in vocab.items())
    topc = nlargest(step_size, ((f, w) for w,f,_ in candidates.items()))
    for f,c in topc:
        vocab.increment(c, f)

    # Second phase, best segmentation with respect to frequences
    # ??? closing condition
    step = 0
    while True:
        step += 1
        nextvocab, candid = vocab_from_segments(allwords, vocab)
        topc = nlargest(step_size, ((f, w) for w,f,_ in candid.items()))
        if not topc:
            break
        for f,c in topc:
            nextvocab.increment(c, f)
    
        ## ??? filter out low freq items from vocab
        min_added_freq = topc[-1][0]
        vocab = Trie()
        n = 0
        for s,f,_ in nextvocab.items():
            if len(s) > 1 and f < min_added_freq:
                continue
            vocab.increment(s, f)
            n += 1
        # add single bytes missing from tokenisation
        for b in singles:
            if vocab.get_freq(b) is None:
                vocab.increment(b, 1)
                n += 1
        print(step, n, min_added_freq,
              [(''.join(s), f) for (f,s) in topc[:5]])
        if n > vocab_size:
            break

    return vocab


def tokenize_string(instr, vocab):
    toks = []
    for w in instr.split(' '):
        toks.extend(best_toks(w, vocab))
    return toks


def tokenize_file(infile, vocab, output):
    for line in infile:
        output.write(' '.join(tokenize_string(line[:-1], vocab)))
        output.write('\n')


def usage():
    print('usage: hftoks.py learn INTEXTFILE OUTVOCABFILE [VOCAB_SIZE [STEP_SIZE]]')
    print('       hftoks.py tokenize VOCABFILE < INTEXT > OUTTOKENS')
    sys.exit(1)


if __name__ == '__main__':
    if not sys.argv[2:]:
        usage()
    if sys.argv[1] not in ('learn', 'tokenize'):
        usage()
    if sys.argv[1] == 'learn':
        if not sys.argv[3:]:
            usage()
        vocab_size = 3000
        if sys.argv[4:]:
            vocab_size = int(sys.argv[4])
        step_size = int(vocab_size / 20)
        if sys.argv[5:]:
            step_size = int(sys.argv[5])
        words = open(sys.argv[2], encoding='utf8').read().split()
        vocab = process_text(words, vocab_size=vocab_size, step_size=step_size)
        voclist = [(f,w) for (w,f,_) in vocab.items()]
        voclist.sort(reverse=True)
        # XXX filter out lowfreq non-one-byte items above vocab_size
        with open(sys.argv[3], 'w', encoding='utf8') as out:
            for f, w in voclist:
                out.write('%s\t%d\n' % (''.join(w),f))

    else: # tokenize
        vocab = read_vocab(sys.argv[2])
        tokenize_file(sys.stdin, vocab, sys.stdout)

        
    
