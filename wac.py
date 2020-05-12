import os
import json
import re
with open('selected_tropes.txt', 'r') as f:
    selected_tropes = [line[:-1] for line in f.readlines()]

all_chars = []
for file in os.listdir("crawled"):
    filepath = os.path.join("crawled", file)
    chars = json.load(open(filepath))
    all_chars.extend(chars['data'])

all_tropes_desc = {}
for c in all_chars:
    for t in c['tropes']:
        if t['trope_type'] in all_tropes_desc:
            all_tropes_desc[t['trope_type']].append(t['trope_description'])
        else:
            all_tropes_desc[t['trope_type']] = [t['trope_description']]


def preprocess_sent(sent):
    sent = re.sub(r"[^A-z0-9 ']", "", sent)
    # sent = sent.lower()
    # sent = re.sub('\d+',"<NUM>", sent)
    # sent = tokenizer(sent)
    return sent
# preprocess_sent("She frequently derides 69 Sena's 'cow udders', which are the source of her nickname 'Meat'. One of their early arguments had")


for i, trope in enumerate(selected_tropes):
    with open(f'raw_data.csv', 'a+') as f:
        for sent in all_tropes_desc[trope]:
            sent = preprocess_sent(sent)
            if sent and len(sent.split()) < 256:
                f.write(f"{i},{sent}\n")
