#-*- coding:utf-8 -*-
from DemoRe.emb_builder import EmbeddingBuilder
emb_builder = EmbeddingBuilder('retrieval_models/sentence-transformers/all-mpnet-base-v2')
from DemoRe.text_modifier import EntityAnonymizer
# initialize the anonymizer with NER model
anonymizer = EntityAnonymizer('retrieval_models/flair/ner-english-ontonotes-large/pytorch_model.bin')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

import os
import json
import numpy as np
from tqdm import tqdm
# dataset list
dataset_name_list = ['ADE'] # TODO: add datasets here

datapath = 'RE' # TODO: add task here
# build embedding
for dataset_name in dataset_name_list:
    logging.info('Building embedding for dataset: {}'.format(dataset_name))
    dataset = json.load(open(os.path.join(datapath, dataset_name + '/train.json'), encoding='utf-8'))
    logging.info('Training dataset size: {}'.format(len(dataset)))
    
    sentence_embs = []
    anonymized_sentence_embs = []
    entity_only_embs = []
    for unit in tqdm(dataset, desc='Building embedding for dataset: {}'.format(dataset_name)):
        sentence = unit['sentence']
        anonymized_sentence = anonymizer.anonymize(sentence)
        entity_list = anonymizer.get_entity_list(sentence)
        entity_only = ' '.join(entity_list)
        
        sentence_embs.append(emb_builder.get_mean_pooling_embedding(sentence).squeeze().cpu().numpy())
        anonymized_sentence_embs.append(emb_builder.get_mean_pooling_embedding(anonymized_sentence).squeeze().cpu().numpy())
        entity_only_embs.append(emb_builder.get_mean_pooling_embedding(entity_only).squeeze().cpu().numpy())
        
    sentence_embs = np.array(sentence_embs)
    anonymized_sentence_embs = np.array(anonymized_sentence_embs)

    # save embedding
    with open(os.path.join(datapath, dataset_name + '/train_question_embs.npy'), 'wb') as f:
        np.save(f, sentence_embs)
    
    with open(os.path.join(datapath, dataset_name + '/train_question_embs_anonymized.npy'), 'wb') as f:
        np.save(f, anonymized_sentence_embs)
        