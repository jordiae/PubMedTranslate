import os
import ntpath
import xml.etree.ElementTree as ET
import tempfile
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

sys.stdout = open(os.path.join(OUTPUT_PATH, 'log.txt'), 'w')


def get_mesh2decs_dict(decs_codes_path):
    lines = decs_codes_path.readlines()
    mesh2decs_dict = {}
    for line in lines:
        decs_code, _, _, mesh_code, _, = line.split('\t')
        mesh2decs_dict[mesh_code] = decs_code
    return mesh2decs_dict


def read_xmls(xml_paths):
    xmls = {}
    for xml_path in xml_paths:
        if xml_path[-2:] != 'gz':
            xmls[ntpath.basename(xml_path)] = open(xml_path, 'r')
        else:
            xmls[ntpath.basename(xml_path)[:-3]] = gzip.open(xml_path, 'r')
    return xmls


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
            issn_node = pubmedarticle.find('MedlineCitation').find('Article').find('Journal').find('ISSN')  # pubmedarticle[0][3][0][0]
            journal = issn_node.text
            # title
            articletitle_node = pubmedarticle.find('MedlineCitation').find('Article').find('ArticleTitle')  # [0][3][1]
            title = articletitle_node.text
            # year
            year_node = pubmedarticle.find('MedlineCitation').find('Article').find('Journal').find('JournalIssue').find('PubDate').find('Year')  # pubmedarticle[0][3][0][1][2][0]
            year = year_node.text
            # abstractText
            abstracttext_node = pubmedarticle.find('MedlineCitation').find('Article').find('Abstract').find('AbstractText')  # [0][3][3][0]
            abstractText = {'ab_es': abstracttext_node.text}
            # decsCodes
            meshheading_nodes = pubmedarticle.find('MedlineCitation').find('MeshHeadingList').find('MeshHeading')
            decsCodes = []
            for meshheading in meshheading_nodes:
                ui = meshheading.attrib['UI']
                decsCodes.append(mesh2decs_dict[ui])
            parsed_xml.append(dict(journal=journal, title=title, id = id_, decsCodes=decsCodes, year=year, \
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
        parsed_xmls[filename] = parse_xml(filename, xml, mesh2decs_dict)
    return parsed_xmls


def split_sentences(text):
    directory = os.getcwd()
    os.chdir(GENIASS_PATH)
    input_tempfile = tempfile.NamedTemporaryFile()
    output_tempfile = tempfile.NamedTemporaryFile()
    with open(input_tempfile.name, 'w') as f:
        f.write(text)
    os.system('./' + GENIASS_EX + ' ' + input_tempfile.name + ' ' + output_tempfile.name + ' >/dev/null 2>&1')
    split = []
    with open(output_tempfile.name, 'r') as f:
        split = f.readlines()
    input_tempfile.close()
    output_tempfile.close()
    os.chdir(directory)
    return split


def inverse_splitlines(lines):
    s = ''
    for line in lines:
        s += line + '\n'
    return s


def collect_sentences(parsed_xmls):
    sentences2translate = []
    for index_xml, parsed_xml in enumerate(parsed_xmls):
        for index_article, article in enumerate(parsed_xmls[parsed_xml]):
            print('Collecting sentences from article', index_article + 1, 'of', len(parsed_xmls[parsed_xml]), 'in', \
                  parsed_xml, '(', index_xml, '/', len(parsed_xmls), ')', flush=True)
            sentences2translate.append(article['title'])
            for sentence in split_sentences(article['abstractText']['ab_es']):
                sentences2translate.append(sentence)
    return sentences2translate


def collect_sentences_from_parsed_xmls(parsed_xmls):
    sentences2translate = collect_sentences(parsed_xmls)
    sentences_path = os.path.join(TEMP_PATH, 'sentences_en.src')
    with open(sentences_path, 'w') as f:
        f.write(inverse_splitlines([s.strip() for s in sentences2translate]))


def main():
    t0 = time.time()
    mesh2decs_dict = get_mesh2decs_dict(open(DeCS_CODES_PATH, 'r'))
    xml_paths = [os.path.join(PUBMED_XMLS_PATH, path) for path in sorted(os.listdir(PUBMED_XMLS_PATH))]
    xmls = read_xmls(xml_paths)
    parsed_xmls = parse_xmls(xmls, mesh2decs_dict)
    collect_sentences_from_parsed_xmls(parsed_xmls)
    t1 = time.time()
    print('Ellapsed', t1-t0, flush=True)


if __name__ == '__main__':
    main()
