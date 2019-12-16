from glob import glob
import pickle
import os
import ntpath
ntpath.basename("a/b/c")

OUTPUT_PATH = '/data/Jordi/PubmedTranslate/output/'
MAP_PATH = os.path.join(OUTPUT_PATH, 'translated_sentences_idx_map.p')


def main():
    translated_sentences_idx_map = {}
    cumulative = 0
    for filename in sorted(glob(OUTPUT_PATH + 'temp/pubmed*')):
        with open(filename, 'r') as file:
            lines = len(file.readlines())
            translated_sentences_idx_map[ntpath.basename(filename).split('___')[0]] = (cumulative, cumulative + lines)  # cumulative:lines
            cumulative += lines
    pickle.dump(translated_sentences_idx_map, open(MAP_PATH, 'wb'))


if __name__ == '__main__':
    main()