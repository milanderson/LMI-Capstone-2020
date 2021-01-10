import os, re
import xml.etree.ElementTree as ET

USAGE = '''
    Usage:
        skos2solr.py input [savepath]
    Description:
        converts a SKOS dictionary into a set of SOLR synonym rules
    Arguments:
        input
            An filepath or XML formatted string
        savepath (Optional)
            The filepath to save results to
'''

class SKOSParseException(Exception):
    def __init__(self, text):
        super().__init__("Could not Parse SKOS data: " + text)

class skos2solr():
    """
        Converts SKOS dictionaries into a SOLR synonym list
    """

    def __init__(self):
        pass

    def buildSOLR(self, concepts):
        """
            Convert a list of SKOS concepts into SOLR synonym rule text

            Args:
                concepts: a list of SKOS concepts

            Returns:
                rules: SOLR synonym rule string
        """
        rules = ""
        for c in concepts:
            try:
                reflectives = [lab + app for lab in c.labels for app in '12']
                rules += ", ".join(c.labels) + " => " + ", ".join(reflectives + c.synonyms + c.broader + c.narrower) + '\n'
            except Exception as e:
                print(c.XMLNode.tag, c.XMLNode.attrib)
                raise e
        return rules

    def parseSKOS(self, dataSource):
        """
            Load a SKOS XML file or string into a list of Concept objects

            Args:
                dataSource: a SKOS XML file or string

            Returns:
                concepts: a list of SKOS concepts
        """
        # load dataSource from file if provided
        if type(dataSource) is not str:
            raise SKOSParseException("Data source must be a valid XML string or XML file path.")
        if os.path.isfile(dataSource):
            dataSource = open(dataSource, 'r').read()

        # parse XML data
        try:
            root = ET.fromstring(dataSource)
        except Exception as e:
            raise SKOSParseException("Could not read XML data. " + e.__str__())
        
        concepts = [Concept(node) for node in root.getchildren()]
        return concepts

    def __call__(self, dataSource, outPath='synonyms.solr'):
        """
            Convert a a SKOS XML file or string into SOLR synonym rule text and save to file

            Args:
                dataSource: a SKOS XML file or string
                outPath: OPTIONAL. A file path. Defaults to 'synonyms.solr'
        """
        concepts = self.parseSKOS(dataSource)
        rules = self.buildSOLR(concepts)
        f = open(outPath, 'w')
        f.write(rules)
        f.close()


class Concept():
    """
        A container class for a SKOS concept with parsing logic for SKOS XML format
    """

    def __init__(self, XMLNode):
        self.XMLNode = XMLNode
        self.broader = []
        self.narrower = []
        self.synonyms = []
        XMLproperties = XMLNode.getchildren()
        for p in XMLproperties:
            propName = p.tag[p.tag.rfind('}') + 1:]
            print(propName)
            if propName == 'prefLabel':
                self.labels = Concept._split(p.text)
            elif propName == 'broader':
                self.broader += Concept._split(p.text, '1')
            elif propName == 'narrower':
                self.narrower += Concept._split(p.text, '2')
            elif propName == 'synonym':
                self.synonyms += Concept._split(p.text, '1')
                self.synonyms += Concept._split(p.text, '2')

    @staticmethod
    def _split(text, appendor=''):
        words = [word + appendor for word in re.split('; | (| )|, ', text) if word]
        extra = []
        for w in words:
            if '(' in w and w[w.find('(') + 1:w.find('(') + 2].lower() in 'qwertyuiopasdfghjklzxcvbnm':
                extra.append(w.replace('(','').replace(')',''))
        return words + extra

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(USAGE)
    else:
        converter = skos2solr()
        if len(sys.argv) == 3:
            converter(sys.argv[1], sys.argv[2])
        else:
            converter(sys.argv[1])
