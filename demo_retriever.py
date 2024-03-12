from DemoRe.emb_builder import EmbeddingBuilder
emb_builder = EmbeddingBuilder('retrieval_models/sentence-transformers/all-mpnet-base-v2')
from DemoRe.text_modifier import EntityAnonymizer
anonymizer = EntityAnonymizer('retrieval_models/flair/ner-english-ontonotes-large/pytorch_model.bin')
import json
from DemoRe.demo_retriever import DemoRetriever
import numpy as np
import logging

def demo_retriever(sentence, task, dataset, strategy, num):
    # load demos
    demos = json.load(open(task+'/'+dataset+'/train.json','r'))
    
    if strategy == 'sentence_emb':
        demo_embs = np.load(open(task+'/'+dataset+'/train_question_embs.npy','rb'))
        demo_retriever = DemoRetriever(demo_embs,demos,device='cuda:2')
        query_emb = emb_builder.get_mean_pooling_embedding(sentence).squeeze().cpu().numpy()
    elif strategy == 'anonymized_sentence_emb':
        demo_embs = np.load(open(task+'/'+dataset+'/train_question_embs_anonymized.npy','rb'))
        demo_retriever = DemoRetriever(demo_embs,demos,device='cuda:2')
        anonymized_sentence = anonymizer.anonymize(sentence)
        query_emb = emb_builder.get_mean_pooling_embedding(anonymized_sentence).squeeze().cpu().numpy()
    elif strategy == 'entity_only_emb':
        demo_embs = np.load(open(task+'/'+dataset+'/train_entity_only_embs.npy','rb'))
        demo_retriever = DemoRetriever(demo_embs,demos,device='cuda:2')
        entity_list = anonymizer.get_entity_list(sentence)
        entity_only = ' '.join(entity_list)
        query_emb = emb_builder.get_mean_pooling_embedding(entity_only).squeeze().cpu().numpy()

    retrieved_demos = demo_retriever.retrieve(query_emb,topk=num)
    return retrieved_demos