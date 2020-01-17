import json
import os

JSONS_PATH = '/data/Jordi/PubmedTranslate/final/jsons'  # 'output/jsons'
TRANSLATED_SENTENCES_PATH = '/data/Jordi/PubmedTranslate/final_finalv1/final_final/all_translated.txt' # 'output/temp/pubmed19n0128.xml___sentences_en.src'


def lazy_read(fd):
    with open(fd) as f:
        for line in f:
            yield line


def get_n_lines(gen, n):
    lines = []
    for i in range(0, n):
        lines.append(next(gen))
    return lines


def lazy_main():
    translated_sentences_gen = lazy_read(TRANSLATED_SENTENCES_PATH)
    json_paths = [os.path.join(JSONS_PATH, path) for path in sorted(os.listdir(JSONS_PATH))]
    # sent_idx = 0
    for idx, json_path in enumerate(json_paths):
        print('Inserting translated sentences in json', idx + 1, 'of', len(json_paths))
        j = json.loads(open(json_path, 'r').read())
        for art_idx, article in enumerate(j['articles']):
            n_sentences = int(j['articles'][art_idx]['N_sentences'])
            try:
                if n_sentences > 0:
                    sent_article = get_n_lines(translated_sentences_gen, n_sentences) # translated_sentences[sent_idx:sent_idx+n_sentences]
                    if len(j['articles'][art_idx]['title']) > 0:
                        j['articles'][art_idx]['title_es'] = ''.join(sent_article[0].split()).replace('\u2581', ' ')#sent_article[0].strip().replace('\u2581', ' ')
                    if n_sentences > 1:
                        j['articles'][art_idx]['abstractText']['ab_es'] = ''
                        for sent in sent_article[1:]:
                            j['articles'][art_idx]['abstractText']['ab_es'] += ''.join(sent.split()).replace('\u2581', ' ')
                        #j['articles'][art_idx]['abstractText']['ab_es'] =
                            #''.join(sent_article[1:]).replace('\n', ' ')\
                            #.strip().replace('\u2581', ' ')
            except:
                pass
            # sent_idx += n_sentences
        json_string = json.dumps(j)
        with open(os.path.join(json_path), 'w') as f:
            f.write(json_string)


def main():
    json_paths = [os.path.join(JSONS_PATH, path) for path in sorted(os.listdir(JSONS_PATH))]
    translated_sentences = open(TRANSLATED_SENTENCES_PATH, 'r').readlines()
    sent_idx = 0
    for idx, json_path in enumerate(json_paths):
        print('Inserting translated sentences in json', idx + 1, 'of', len(json_paths))
        j = json.loads(open(json_path, 'r').read())
        for art_idx, article in enumerate(j['articles']):
            n_sentences = int(j['articles'][art_idx]['N_sentences'])
            if n_sentences > 0:
                sent_article = translated_sentences[sent_idx:sent_idx+n_sentences]
                if len(j['articles'][art_idx]['title']) > 0:
                    j['articles'][art_idx]['title_es'] = sent_article[0].strip().replace('\u2581', ' ')
                if n_sentences > 1:
                    j['articles'][art_idx]['abstractText']['ab_es'] = ''.join(sent_article[1:]).replace('\n', ' ')\
                        .strip().replace('\u2581', ' ')
            sent_idx += n_sentences
        json_string = json.dumps(j)
        with open(os.path.join(json_path), 'w') as f:
            f.write(json_string)
        return


if __name__ == '__main__':
    # main()
    lazy_main()
