import json
import os

JSONS_PATH = 'output/jsons'
TRANSLATED_SENTENCES_PATH = ''


def main():
    json_paths = [os.path.join(JSONS_PATH, path) for path in sorted(os.listdir(JSONS_PATH))]
    translated_sentences = open(TRANSLATED_SENTENCES_PATH, 'r').readlines()
    sent_idx = 0
    for json_path in json_paths:
        j = json.loads(open(json_path, 'r').read())
        for art_idx, article in enumerate(j['articles']):
            n_sentences = int(j['articles'][art_idx]['N_sentences'])
            if n_sentences > 0:
                sent_article = translated_sentences[sent_idx:sent_idx+n_sentences]
                if len(j['articles'][art_idx]['title_en']) > 0:
                    j['articles'][art_idx]['title_es'] = sent_article[0]
                if n_sentences > 1:
                    j['articles'][art_idx]['abstractText']['ab_es'] = sent_article[1:]
            sent_idx += n_sentences
        json_string = json.dumps(j)
        with open(os.path.join(json_path), 'w') as f:
            f.write(json_string)


if __name__ == '__main__':
    main()
