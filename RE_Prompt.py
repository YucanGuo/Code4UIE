'''
# 1 Stage Prompt for RE
[Base Class Definitions of Entity and Relation]
[Entity Definitions]
[Relation Definitions]
{In-context Examples}
"""
List all the relations in the following sentence as instances of corresponding subclass of class Relation.
"{sentence}"
"""
'''

'''
# 2 Stage Prompt for RE
Stage 1:
[Base Class Definitions of Entity and Relation]
[Entity Definitions]
[Relation Definitions]
{In-context Examples}
"""
List all the subclass of class Relation in the following sentence as an import statement.
"{sentence}"
from Relation import
"""

Stage 2:
[Base Class Definition of Entity and Relation]
[Definitions of Entities be Imported]
[Definitions of Relations be Imported]
{In-context Examples}
"""
List all the relations in the following sentence that belong to the aformentioned Relation subclass as instances of them.
"{sentence}" 
"""
'''

import json
from demo_retriever import demo_retriever
import random
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
        incontext_examples = demo_retriever(sentence, 'RE', args.dataset, args.retrieval_strategy, args.incontext_examples_num)
    if args.dataset == 'ADE':
        for example in incontext_examples:
            prompt['prompt_1'] += '"""\nList all the relations in the following sentence as instances of class Adverse_Effect(Relation).\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_1'] += example['code_1'] + '\n\n'
    elif args.dataset == 'ACE05':
        for example in incontext_examples:
            prompt['prompt_1'] += '"""\nList all the relations in the following sentence as instances of corresponding subclass of class Relation. If there do not exist any relations that belong to the Relation subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_1'] += example['code_1'] + '\n\n'
            prompt['prompt_2']['stage_1'] += '"""\nList all the subclass of class Relation in the following sentence as an import statement. If there do not exist any Relation subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_2']['stage_1'] += example['code_2'] + '\n\n'
            prompt['prompt_2']['stage_2'] += '"""\nList all the relations in the following sentence that belong to the aformentioned Relation subclass as instances of them.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_2']['stage_2'] += example['code_1'] + '\n\n'
    else:
        for example in incontext_examples:
            prompt['prompt_1'] += '"""\nList all the relations in the following sentence as instances of corresponding subclass of class Relation.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_1'] += example['code_1'] + '\n\n'
            prompt['prompt_2']['stage_1'] += '"""\nList all the subclass of class Relation in the following sentence as an import statement.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_2']['stage_1'] += example['code_2'] + '\n\n'
            prompt['prompt_2']['stage_2'] += '"""\nList all the relations in the following sentence that belong to the aformentioned Relation subclass as instances of them.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
            prompt['prompt_2']['stage_2'] += example['code_1'] + '\n\n'
    return prompt

def prompt_construction(relations: dict):
    prompt_1 = ''
    prompt_2 = {'stage_1': '', 'stage_2': ['', '']}
    base_class_defs = json.load(open('RE/' + args.dataset + '/class_defs_json/Base_Class.json'))
    entity_defs = json.load(open('RE/' + args.dataset + '/class_defs_json/Entity.json'))
    relation_defs = json.load(open('RE/' + args.dataset + '/class_defs_json/Relation.json'))
    incontext_examples = add_incontext_examples(relations['sentence'], incontext_examples_num) #{prompt_1: '', prompt_2: {stage_1: '', stage_2: ''}}
    #construct one-stage prompt
    prompt_1 += base_class_defs['Entity'] + '\n\n' + base_class_defs['Relation'] + '\n\n'
    if args.dataset != 'ADE':
        for entity in entity_defs:
            prompt_1 += entity_defs[entity] + '\n\n'
    for relation in relation_defs:
        prompt_1 += relation_defs[relation] + '\n\n'
    prompt_1 += incontext_examples['prompt_1']
    if args.dataset == 'ADE':
        prompt_1 += '"""\nList all the relations in the following sentence as instances of class Adverse_Effect(Relation).\n\"{}\"\n"""'.format(relations['sentence'])
    elif args.dataset == 'ACE05':
        prompt_1 += '"""\nList all the relations in the following sentence as instances of corresponding subclass of class Relation. If there do not exist any relations that belong to the Relation subclasses we defined, print "None".\n\"{}\"\n"""'.format(relations['sentence'])
    else:
        prompt_1 += '"""\nList all the relations in the following sentence as instances of corresponding subclass of class Relation.\n\"{}\"\n"""'.format(relations['sentence'])
    
    #construct two-stage prompt
    if args.dataset != 'ADE':
        prompt_2['stage_1'] += base_class_defs['Entity'] + '\n\n' + base_class_defs['Relation'] + '\n\n'
        for entity in entity_defs:
            prompt_2['stage_1'] += entity_defs[entity] + '\n\n'
        for relation in relation_defs:
            prompt_2['stage_1'] += relation_defs[relation] + '\n\n'
        prompt_2['stage_1'] += incontext_examples['prompt_2']['stage_1']
        if args.dataset == 'ACE05':
            prompt_2['stage_1'] += '"""\nList all the relations in the following sentence as instances of corresponding subclass of class Relation. If there do not exist any relations that belong to the Relation subclasses we defined, print "None".\n\"{}\"\n"""'.format(relations['sentence']) + '\n'
        else:
            prompt_2['stage_1'] += '"""\nList all the subclass of class Relation in the following sentence as an import statement.\n\"{}\"\n"""'.format(relations['sentence']) + '\n'
        prompt_2['stage_1'] += 'from Relation import'
        prompt_2['stage_2'][0] += base_class_defs['Entity'] + '\n\n' + base_class_defs['Relation'] + '\n\n'
        prompt_2['stage_2'][1] += incontext_examples['prompt_2']['stage_2']
        prompt_2['stage_2'][1] += '"""\nList all the relations in the following sentence that belong to the aformentioned Relation subclass as instances of them.\n\"{}\"\n"""'.format(relations['sentence'])
    return prompt_1, prompt_2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='NYT')
    parser.add_argument('--test_file', type=str, default='RE/NYT/test.json')
    parser.add_argument('--train_file', type=str, default='RE/NYT/train.json')
    parser.add_argument('--retrieval_strategy', type=str, default='anonymized_sentence_emb', choices=['random', 'sentence_emb', 'anonymized_sentence_emb', 'entity_only_emb'])
    parser.add_argument('--output_file', type=str, default='RE/NYT/prompt/RE-nyt-1&2stage-code-ase-15.json')
    parser.add_argument('--incontext_examples_num', type=int, default=15)
    args = parser.parse_args()
    incontext_examples_num = args.incontext_examples_num
    incontext_examples_dir = args.train_file
    with open(args.test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    RE_prompt = []
    for RE_data in test_data:    
        one_stage_prompt, two_stage_prompt = prompt_construction(RE_data)
        prompt = RE_data
        prompt['prompt_1'] = one_stage_prompt
        prompt['prompt_2'] = two_stage_prompt
        RE_prompt.append(prompt)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(RE_prompt, f, ensure_ascii=False, indent=2)