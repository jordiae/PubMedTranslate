from glob import glob

OUTPUT_PATH = '/data/Jordi/PubmedTranslate/output/'


def main():
    with open('all_sentences.src', 'w') as outfile:
        for filename in sorted(glob(OUTPUT_PATH + 'temp/pubmed*')):
            with open(filename) as infile:
                for line in infile:
                    outfile.write(line)


if __name__ == '__main__':
    main()