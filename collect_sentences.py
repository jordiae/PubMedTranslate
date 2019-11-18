import os
import ntpath
import xml.etree.ElementTree as ET
import gzip
import time
import sys

PUBMED_XMLS_PATH = '/data/MESINESP/pubmed_training/baseline_pubed_xmls'
# PUBMED_XMLS_PATH = os.path.join('data', 'pubmed_xmls')
DeCS_CODES_PATH = os.path.join('data', 'DeCS', 'DeCS.2019.both.v3.tsv')
OUTPUT_PATH = os.path.join('output')
GENIASS_PATH = os.path.join('bin', 'geniass')
GENIASS_EX = 'geniass'
TEMP_PATH = os.path.join('output', 'temp')

START_AT = None
END_AT = None
if len(sys.argv[1:]) > 2:
    START_AT = sys.argv[1]
    END_AT = sys.argv[2]
NAME = ''
if START_AT is not None:
    NAME += START_AT + '___'
if END_AT is not None:
    if len(NAME) == 0:
        NAME += '___'
    NAME += + END_AT + '___'

sys.stdout = open(os.path.join(OUTPUT_PATH, NAME + 'log.txt'), 'w')
sys.stderr = open(os.path.join(OUTPUT_PATH, NAME + 'err.txt'), 'w')


def get_mesh2decs_dict(decs_codes_path):
    lines = decs_codes_path.readlines()
    mesh2decs_dict = {}
    for line in lines:
        decs_code, _, _, mesh_code, _, = line.split('\t')
        mesh2decs_dict[mesh_code] = decs_code
    return mesh2decs_dict


def read_xmls(xml_paths, start_at=None, end_at=None):
    # start_at and end_at both included
    xmls = {}
    work = False
    if start_at is None:
        work = True
    skip_count = 0
    end = False
    for xml_path in xml_paths:
        if xml_path[-2:] != 'gz':
            if end_at is not None and ntpath.basename(xml_path) == end_at:
                end = True
            if start_at is not None and ntpath.basename(xml_path) == start_at:
                work = True
            if work:
                xmls[ntpath.basename(xml_path)] = open(xml_path, 'r')
            else:
                skip_count += 1
        else:
            if end_at is not None and ntpath.basename(xml_path) == end_at:
                end = True
            if start_at is not None and ntpath.basename(xml_path)[:-3] == start_at:
                work = True
            if work:
                xmls[ntpath.basename(xml_path)[:-3]] = gzip.open(xml_path, 'r')
            else:
                skip_count += 1
        if end:
            break
    return xmls, skip_count


def parse_xml(filename, xml, mesh2decs_dict):
    tree = ET.parse(xml)
    root = tree.getroot()
    parsed_xml = []
    skip = 0
    print('Parsing', filename, flush=True)
    for index, pubmedarticle in enumerate(root):
        try:
            # id
            pmid_node = pubmedarticle.find('MedlineCitation').find('PMID')  # pubmedarticle[0][0]
            id_ = pmid_node.text
            # journal
            # pubmedarticle[0][3][0][0]
            issn_node = pubmedarticle.find('MedlineCitation').find('Article').find('Journal').find('ISSN')
            journal = issn_node.text
            # title
            articletitle_node = pubmedarticle.find('MedlineCitation').find('Article').find('ArticleTitle')  # [0][3][1]
            title = articletitle_node.text
            # year
            year_node = pubmedarticle.find('MedlineCitation').find('Article').find('Journal').find('JournalIssue').\
                find('PubDate').find('Year')  # pubmedarticle[0][3][0][1][2][0]
            year = year_node.text
            # abstractText
            abstracttext_nodes = pubmedarticle.find('MedlineCitation').find('Article').find('Abstract').\
                findall('AbstractText')  # [0][3][3][0]
            text = ''
            for abstracttext_node in abstracttext_nodes:
                text += abstracttext_node.text + ' '
            abstractText = {'ab_en': text}
            # decsCodes
            meshheading_nodes = pubmedarticle.find('MedlineCitation').find('MeshHeadingList').find('MeshHeading')
            decsCodes = []
            for meshheading in meshheading_nodes:
                ui = meshheading.attrib['UI']
                decsCodes.append(mesh2decs_dict[ui])
            parsed_xml.append(dict(journal=journal, title=title, id = id_, decsCodes=decsCodes, year=year,
                              abstractText=abstractText))
        except BaseException as e:
            # print('Skipping article', index, 'at', filename)
            skip += 1
            continue
    print('Skipped', skip, 'articles of', len(root), flush=True)
    return parsed_xml


def parse_xmls(xmls, mesh2decs_dict):
    parsed_xmls = {}
    for filename, xml in xmls.items():
        #parsed_xmls[filename] = parse_xml(filename, xml, mesh2decs_dict)
        yield filename, parse_xml(filename, xml, mesh2decs_dict)
    #return parsed_xmls


def split_sentences(text):
    if text is None:
        return []
    directory = os.getcwd()
    os.chdir(GENIASS_PATH)
    input_filenane = NAME + 'splitter_in.txt'
    output_filename = NAME + 'splitter_out.txt'
    with open(input_filenane, 'w') as f:
        f.write(text)
    with open(output_filename, 'w') as f:
        f.write('')
    os.system('./' + GENIASS_EX + ' ' + input_filenane + ' ' + output_filename + ' >/dev/null 2>&1')
    split = []
    with open(output_filename, 'r') as f:
        split = f.readlines()
    os.chdir(directory)
    return split


def inverse_splitlines(lines):
    s = ''
    for line in lines:
        s += line + '\n'
    return s


def collect_sentences(xmls, mesh2decs_dict, skip_count=0):
    # saved_filename = NAME + 'sentences_en.src'
    # sentences2translate = []
    for index_xml, (filename, parsed_xml) in enumerate(parse_xmls(xmls, mesh2decs_dict)):
        sentences2translate = []
        for index_article, article in enumerate(parsed_xml):
            print('Collecting sentences from article', index_article + 1, 'of', len(parsed_xml), 'in',
                  filename, '(', index_xml + skip_count + 1, '/', len(xmls) + skip_count, ')', flush=True)
            sentences2translate.append(article['title'])
            for sentence in split_sentences(article['abstractText']['ab_en']):
                sentences2translate.append(sentence)
        sentences_path = os.path.join(TEMP_PATH, filename + '___sentences_en.src')
        with open(sentences_path, 'a') as f:
            non_none_sentences2translate = [s for s in sentences2translate if s is not None]
            if len(non_none_sentences2translate) > 0:
                f.write(inverse_splitlines([s.strip() for s in non_none_sentences2translate]))
    # return sentences2translate


def collect_sentences_from_parsed_xmls(parsed_xmls):
    pass
    #collect_sentences(parsed_xmls)
    # sentences2translate = collect_sentences(parsed_xmls)
    # sentences_path = os.path.join(TEMP_PATH, 'sentences_en.src')
    # with open(sentences_path, 'w') as f:
    #   f.write(inverse_splitlines([s.strip() for s in sentences2translate]))


def main():
    t0 = time.time()
    mesh2decs_dict = get_mesh2decs_dict(open(DeCS_CODES_PATH, 'r'))
    xml_paths = [os.path.join(PUBMED_XMLS_PATH, path) for path in sorted(os.listdir(PUBMED_XMLS_PATH))]
    xmls, skip_count = read_xmls(xml_paths, start_at=START_AT, end_at=END_AT)
    # parsed_xmls = parse_xmls(xmls, mesh2decs_dict)
    collect_sentences(xmls, mesh2decs_dict, skip_count)
    t1 = time.time()
    print('Ellapsed', t1-t0, flush=True)


if __name__ == '__main__':
    main()
