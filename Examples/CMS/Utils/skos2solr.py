import os, re
import xml.etree.ElementTree as ET

USAGE = '''
    Usage:
        skos2solr.py input mode [savepath]
    Description:
        converts a SKOS dictionary into a set of SOLR synonym rules
    Arguments:
        input
            An filepath or XML formatted string
        mode
            One of "b" / "broader", "n" / "narrower", or "e" / "explosive". Sets the entailment direction to move up, down, or both directions along the SKOS graph.
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
    MODES = ["b", "broader", "n", "narrower", "e", "explosive"]

    def __init__(self):
        pass

    def buildSOLR(self, concepts, mode):
        """
            Convert a list of SKOS concepts into SOLR synonym rule text

            Args:
                concepts: a list of SKOS concepts

            Returns:
                rules: SOLR synonym rule string
        """
        rules = ""
        for c in concepts:
            # since Lucene synonyms are processed greedily, we must sort to prevent chain entailment
            if mode == "n" or mode == "narrower":
                conceptDict = {l:c for c in concepts for l in c.labels}
                sortedConcepts = [c for c in concepts if not c.narrower]
                i = 0
                while i < len(sortedConcepts):
                    for label in sortedConcepts[i].broader:
                        if label in conceptDict and conceptDict[label] not in sortedConcepts:
                            sortedConcepts.append(conceptDict[label])
                    i +=1
                concepts = sortedConcepts
                concepts.reverse()
            if mode == "b" or mode == "broader":
                conceptDict = {l:c for c in concepts for l in c.labels}
                sortedConcepts = [c for c in concepts if not c.broader]
                i = 0
                while i < len(sortedConcepts):
                    for label in sortedConcepts[i].narrower:
                        if label in conceptDict and conceptDict[label] not in sortedConcepts:
                            sortedConcepts.append(conceptDict[label])
                    i +=1
                concepts = sortedConcepts
                concepts.reverse()

            try:
                if mode == "e" or mode == "explosive":
                    rules += ", ".join(c.labels) + " => " + ", ".join(c.labels + c.synonyms + c.broader + c.narrower) + '\n'
                if mode == "n" or mode == "narrower":
                    rules += ", ".join(c.labels) + " => " + ", ".join(c.labels + c.synonyms + c.narrower) + '\n'
                if mode == "b" or mode == "broader":
                    rules += ", ".join(c.labels) + " => " + ", ".join(c.labels + c.synonyms + c.broader) + '\n'
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

    def __call__(self, mode, dataSource, outPath='synonyms.solr'):
        """
            Convert a a SKOS XML file or string into SOLR synonym rule text and save to file

            Args:
                dataSource: a SKOS XML file or string
                outPath: OPTIONAL. A file path. Defaults to 'synonyms.solr'
        """
        if not any(mode == m for m in skos2solr.MODES):
            raise ValueError("Mode must be one of: " + " ".join(skos2solr.MODES))

        concepts = self.parseSKOS(dataSource)
        rules = self.buildSOLR(concepts, mode)
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
            if propName == 'prefLabel':
                self.labels = Concept._split(p.text)
            elif propName == 'acronym':
                self.labels += Concept._split(p.text)
            elif propName == 'altLabel':
                self.labels += Concept._split(p.text)
            elif propName == 'broader':
                self.broader += Concept._split(p.text)
            elif propName == 'narrower':
                self.narrower += Concept._split(p.text)
            elif propName == 'synonym':
                self.synonyms += Concept._split(p.text)

    @staticmethod
    def _split(text):
        def replaceParen(w):
            if '(' in w and w[w.find('(') + 1:w.find('(') + 2].lower() in 'qwertyuiopasdfghjklzxcvbnm':
                return w.replace('(','').replace(')','')
            elif w[-1] == ")" and "(" not in w:
                return w[:-1]
            else:
                return w
        return [replaceParen(word) for word in re.split('; | \(|\) |, ', text)]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(USAGE)
    else:
        converter = skos2solr()
        if len(sys.argv) == 4:
            converter(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            converter(sys.argv[1], sys.argv[2])
