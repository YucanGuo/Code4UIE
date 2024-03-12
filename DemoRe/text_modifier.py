from flair.data import Sentence
from flair.models import SequenceTagger
from collections import defaultdict
from copy import deepcopy
class EntityAnonymizer():
    def __init__(self, model_name):
        """
        model_name: the path to the model
        could be downloaded from https://github.com/flairNLP/flair/#state-of-the-art-models
        """
        
        self.model = SequenceTagger.load(model_name)
    
    def anonymize(self, text):
        sentence = Sentence(text)
        self.model.predict(sentence)
        entity_tag_cnt = defaultdict(int)
        anonymized_text = deepcopy(text)
        for entity in sentence.get_spans('ner'):
            anonymized_text = anonymized_text.replace(entity.text,'['+entity.tag+'_'+str(entity_tag_cnt[entity.tag])+']')
            entity_tag_cnt[entity.tag] += 1
        return anonymized_text

    def get_entity_list(self, text):
        sentence = Sentence(text)
        self.model.predict(sentence)
        entity_list = []
        for entity in sentence.get_spans('ner'):
            entity_list.append(entity.text)
        return entity_list
    
if __name__ == '__main__':
    anonymizer = EntityAnonymizer('/data/lyt/models/flair/ner-english-ontonotes-large/pytorch_model.bin')
    print(anonymizer.anonymize('George Washington went to Washington .'))
        