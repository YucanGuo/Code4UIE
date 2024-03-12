'''
# 1 Stage Prompt for NER
[Base Class Definition of Entity]
[Entity Definitions]
{In-context Examples}
"""
List all the Entity words in the following sentence as instances of corresponding subclasses of class Entity. If there do not exist any Entity words that belong to the Entity subclasses we defined, print "None".
"{sentence}"
"""
'''

'''
# 2 Stage Prompt for NER
Stage 1:
[Base Class Definition of Entity]
[Entity Definitions]
{In-context Examples}
"""
List all the subclass of class Entity in the following sentence as an import statement. If there do not exist any Entity subclasses we defined, print "None".
"{sentence}"
from Entity import
"""

Stage 2:
[Base Class Definition of Entity]
[Definitions of Entities be Imported]
{In-context Examples}
"""
List all the Entity words in the following sentence that belong to the aformentioned Entity subclasses as instances of them.
"{sentence}" 
"""
'''

import json
import random
from demo_retriever import demo_retriever
seed = 42
random.seed(seed)
import argparse
incontext_examples_num = 10
incontext_examples_dir = ''

def add_incontext_examples(sentence: str, num: int):
    prompt = {'prompt_1': '', 'prompt_2': {'stage_1': '', 'stage_2': ''}}
    if args.retrieval_strategy == 'random':
        incontext_examples = []
        with open(incontext_examples_dir, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        incontext_examples = random.sample(examples, num)
    else:
        incontext_examples = demo_retriever(sentence, 'NER', args.dataset, args.retrieval_strategy, args.incontext_examples_num)
    for example in incontext_examples:
        prompt['prompt_1'] += '"""\nList all the Entity words in the following sentence as instances of corresponding subclasses of class Entity. If there do not exist any Entity words that belong to the Entity subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_1'] += example['code_1'] + '\n\n'
        prompt['prompt_2']['stage_1'] += '"""\nList all the subclass of class Entity in the following sentence as an import statement. If there do not exist any Entity subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_2']['stage_1'] += example['code_2'] + '\n\n'
        prompt['prompt_2']['stage_2'] += '"""\nList all the Entity words in the following sentence that belong to the aformentioned Entity subclasses as instances of them.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_2']['stage_2'] += example['code_1'] + '\n\n'
    return prompt

def prompt_construction(entities: dict):
    prompt_1 = ''
    prompt_2 = {'stage_1': '', 'stage_2': ['', '']}
    base_class_defs = json.load(open('NER/' + args.dataset + '/class_defs_json/Base_Class.json', encoding='utf-8'))
    entity_defs = json.load(open('NER/' + args.dataset + '/class_defs_json/Entity.json', encoding='utf-8'))
    incontext_examples = add_incontext_examples(entities['sentence'], incontext_examples_num) #{prompt_1: '', prompt_2: {stage_1: '', stage_2: ''}}
    #construct one-stage prompt
    prompt_1 += base_class_defs['Entity'] + '\n\n'
    for entity in entity_defs:
        prompt_1 += entity_defs[entity] + '\n\n'
    prompt_1 += incontext_examples['prompt_1']
    prompt_1 += '"""\nList all the Entity words in the following sentence as instances of corresponding subclasses of class Entity. If there do not exist any Entity words that belong to the Entity subclasses we defined, print "None".\n\"{}\"\n"""'.format(entities['sentence'])
    
    #construct two-stage prompt
    prompt_2['stage_1'] += base_class_defs['Entity'] + '\n\n'
    for entity in entity_defs:
        prompt_2['stage_1'] += entity_defs[entity] + '\n\n'
    prompt_2['stage_1'] += incontext_examples['prompt_2']['stage_1']
    prompt_2['stage_1'] += '"""\nList all the subclass of class Entity in the following sentence as an import statement. If there do not exist any Entity subclasses we defined, print "None".\n\"{}\"\n"""'.format(entities['sentence']) + '\n'
    prompt_2['stage_1'] += 'from Entity import'
    prompt_2['stage_2'][0] += base_class_defs['Entity'] + '\n\n'
    prompt_2['stage_2'][1] += incontext_examples['prompt_2']['stage_2']
    prompt_2['stage_2'][1] += '"""\nList all the Entity words in the following sentence that belong to the aformentioned Entity subclasses as instances of them.\n\"{}\"\n"""'.format(entities['sentence'])
    return prompt_1, prompt_2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='CoNLL03')
    parser.add_argument('--test_file', type=str, default='NER/CoNLL03/test.json')
    parser.add_argument('--train_file', type=str, default='NER/CoNLL03/train.json')
    parser.add_argument('--retrieval_strategy', type=str, default='random', choices=['random', 'sentence_emb', 'anonymized_sentence_emb', 'entity_only_emb'])
    parser.add_argument('--output_file', type=str, default='NER/CoNLL03/prompt/NER-conll03-1&2stage-code-r-10.json')
    parser.add_argument('--incontext_examples_num', type=int, default=10)
    args = parser.parse_args()
    incontext_examples_num = args.incontext_examples_num
    incontext_examples_dir = args.train_file
    with open(args.test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    NER_prompt = []
    for NER_data in test_data:    
        one_stage_prompt, two_stage_prompt = prompt_construction(NER_data)
        prompt = NER_data
        prompt['prompt_1'] = one_stage_prompt
        prompt['prompt_2'] = two_stage_prompt
        NER_prompt.append(prompt)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(NER_prompt, f, ensure_ascii=False, indent=2)