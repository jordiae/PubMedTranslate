import os
import ntpath
import xml.etree.ElementTree as ET
import json
import tempfile
from opennmt_caller import translate_sentence
from concurrent import futures

PUBMED_XMLS_PATH = os.path.join('data', 'pubmed_xmls')
DeCS_CODES_PATH = os.path.join('data', 'DeCS', 'DeCS.2019.both.v3.tsv')
OUTPUT_PATH = os.path.join('output')
GENIASS_PATH = os.path.join('bin', 'geniass')
GENIASS_EX = 'geniass'


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
        xmls[ntpath.basename(xml_path)] = open(xml_path, 'r')
    return xmls


def parse_xml(filename, xml, mesh2decs_dict):
    tree = ET.parse(xml)
    root = tree.getroot()
    parsed_xml = []
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
            print('Skipping article', index, 'at', filename)
            continue
        # break
    return parsed_xml


def parse_xmls(xmls, mesh2decs_dict):
    parsed_xmls = {}
    for filename, xml in xmls.items():
        parsed_xmls[filename] = parse_xml(filename, xml, mesh2decs_dict)
    return parsed_xmls


def split_sentences(text):
    dir = os.getcwd()
    os.chdir(GENIASS_PATH)
    input_tempfile = tempfile.NamedTemporaryFile()
    output_tempfile = tempfile.NamedTemporaryFile()
    with open(input_tempfile.name, 'w') as f:
        f.write(text)
    print(GENIASS_EX + ' ' + input_tempfile.name + ' ' + output_tempfile.name)
    os.system('./' + GENIASS_EX + ' ' + input_tempfile.name + ' ' + output_tempfile.name)
    split = []
    with open(output_tempfile.name, 'r') as f:
        split = f.readlines()
    input_tempfile.close()
    output_tempfile.close()
    os.chdir(dir)
    return split


def translate(sentence):
    src = 'en'
    tgt = 'es'
    opennmt_response = translate_sentence(
        src, tgt, sentence)
    # Because opennmt returns a list of list of dict, we access the [0][0] element
    translated_sentence_dict = opennmt_response.json()[0][0]
    # 'tgt' and 'pred_score' keys are defined in OpenNMT API
    translated_sentence = translated_sentence_dict.get('tgt')
    return translated_sentence


def inverse_splitlines(lines):
    s = ''
    for line in lines:
        s += line + '\n'
    return s


def translate_parsed_xml(parsed_xml):
    translated_parsed_xml = parsed_xml.copy()
    translated_parsed_xml['title'] = translate(parsed_xml['title'])
    sentences = split_sentences(parsed_xml['abstractText']['ab_es'])
    translated_abstract = []
    for sentence in sentences:
        translated_abstract.append(translate(sentence))
    translated_parsed_xml['abstractText'] = inverse_splitlines(translated_abstract)
    return translated_parsed_xml


def translate_parsed_xmls(parsed_xmls):
    translated_parsed_xmls = {}
    for filename, parsed_xml in parsed_xmls.items():
        translated_parsed_xmls[filename] = []
        for article in parsed_xml:
            translated_parsed_xmls[filename].append(translate_parsed_xml(article))
    return translated_parsed_xmls


def write_json(translated_parsed_xmls, output_path):
    for filename, translated_parsed_xml in translated_parsed_xmls.items():
        filename_without_extension = os.path.splitext(filename)[0]
        json_string = json.dumps(translated_parsed_xml)
        with open(os.path.join(output_path, filename_without_extension + '.json'), 'w') as f:
            f.write(json_string)


def main():
    mesh2decs_dict = get_mesh2decs_dict(open(DeCS_CODES_PATH, 'r'))
    xml_paths = [os.path.join(PUBMED_XMLS_PATH, path) for path in os.listdir(PUBMED_XMLS_PATH)]
    xmls = read_xmls(xml_paths)
    parsed_xmls = parse_xmls(xmls, mesh2decs_dict)
    translated_parsed_xmls = translate_parsed_xmls(parsed_xmls)
    write_json(translated_parsed_xmls, OUTPUT_PATH)


if __name__ == '__main__':
    main()