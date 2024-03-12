'''
# 1 Stage Prompt for EE
[Base Class Definitions of Entity and Event]
[Entity Definitions]
[Event Definitions]
{In-context Examples}
"""
List all the events in the following sentence as instances of corresponding subclass of class Event.
"{sentence}"
"""
'''

'''
# 2 Stage Prompt for EE
Stage 1:
[Base Class Definitions of Entity and Event]
[Entity Definitions]
[Event Definitions(annotations only)]
{In-context Examples}
"""
List all the subclass of class Event in the following sentence as an import statement.
"{sentence}"
"""
from Event import

Stage 2:
[Base Class Definition of Entity and Event]
[Definitions of Entities be Imported]
[Definitions of Events be Imported]
{In-context Examples}
"""
List all the events in the following sentence that belong to the aformentioned Event subclass as instances of them.
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

def add_incontext_examples(sentence: str):
    prompt = {'prompt_1': '', 'prompt_2': {'stage_1': '', 'stage_2': ''}}
    if args.retrieval_strategy == 'random':
        incontext_examples = []
        with open(incontext_examples_dir, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        incontext_examples = random.sample(examples, args.incontext_examples_num)
    else:
        incontext_examples = demo_retriever(sentence, 'EE', args.dataset, args.retrieval_strategy, args.incontext_examples_num)
    for example in incontext_examples:
        prompt['prompt_1'] += '"""\nList all the events in the following sentence as instances of corresponding subclass of class Event. If there do not exist any events that belong to the Event subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_1'] += example['code_1'] + '\n\n'
        prompt['prompt_2']['stage_1'] += '"""\nList all the subclass of class Event in the following sentence as an import statement. If there do not exist any Event subclasses we defined, print "None".\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_2']['stage_1'] += example['code_2'] + '\n\n'
        prompt['prompt_2']['stage_2'] += '"""\nList all the events in the following sentence that belong to the aformentioned Event subclass as instances of them.\n\"{}\"\n"""'.format(example['sentence']) + '\n'
        prompt['prompt_2']['stage_2'] += example['code_1'] + '\n\n'
    return prompt

def prompt_construction(events: dict):
    prompt_1 = ''
    prompt_2 = {'stage_1': '', 'stage_2': ['', '']}
    base_class_defs = json.load(open('EE/' + args.dataset + '/class_defs_json/Base_Class.json'))
    if args.dataset in ['ACE05']:
        entity_defs = json.load(open('EE/' + args.dataset + '/class_defs_json/Entity.json'))
    event_defs = json.load(open('EE/' + args.dataset + '/class_defs_json/Event.json'))
    incontext_examples = add_incontext_examples(events['sentence']) #{prompt_1: '', prompt_2: {stage_1: '', stage_2: ''}}
    #construct one-stage prompt
    prompt_1 += base_class_defs['Entity'] + '\n\n' + base_class_defs['Event'] + '\n\n'
    if args.dataset in ['ACE05']:
        for entity in entity_defs:
            prompt_1 += entity_defs[entity] + '\n\n'
    for event in event_defs:
        prompt_1 += event_defs[event] + '\n\n'
    prompt_1 += incontext_examples['prompt_1']
    prompt_1 += '"""\nList all the events in the following sentence as instances of corresponding subclass of class Event. If there do not exist any events that belong to the Event subclasses we defined, print "None".\n\"{}\"\n"""'.format(events['sentence'])
    
    #construct two-stage prompt
    prompt_2['stage_1'] += base_class_defs['Entity'] + '\n\n' + base_class_defs['Event'] + '\n\n'
    if args.dataset in ['ACE05']:
        for entity in entity_defs:
            prompt_2['stage_1'] += entity_defs[entity] + '\n\n'
    for event in event_defs:
        prompt_2['stage_1'] += event_defs[event] + '\n\n' #.split('    def')[0]
    prompt_2['stage_1'] += incontext_examples['prompt_2']['stage_1']
    prompt_2['stage_1'] += '"""\nList all the subclass of class Event in the following sentence as an import statement. If there do not exist any Event subclasses we defined, print "None".\n\"{}\"\n"""'.format(events['sentence']) + '\n'
    prompt_2['stage_1'] += 'from Event import'
    prompt_2['stage_2'][0] += base_class_defs['Entity'] + '\n\n' + base_class_defs['Event'] + '\n\n'
    prompt_2['stage_2'][1] += incontext_examples['prompt_2']['stage_2']
    prompt_2['stage_2'][1] += '"""\nList all the events in the following sentence that belong to the aformentioned Event subclass as instances of them.\n\"{}\"\n"""'.format(events['sentence'])
    return prompt_1, prompt_2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='CASIE')
    parser.add_argument('--test_file', type=str, default='EE/CASIE/test.json')
    parser.add_argument('--train_file', type=str, default='EE/CASIE/train.json')
    parser.add_argument('--retrieval_strategy', type=str, default='anonymized_sentence_emb', choices=['random', 'sentence_emb', 'anonymized_sentence_emb'])
    parser.add_argument('--output_file', type=str, default='EE/CASIE/prompt/EE-casie-2stage-code-ase-10.json')
    parser.add_argument('--incontext_examples_num', type=int, default=10)
    args = parser.parse_args()
    incontext_examples_num = args.incontext_examples_num
    incontext_examples_dir = args.train_file
    with open(args.test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    EE_prompt = []
    for EE_data in test_data:    
        one_stage_prompt, two_stage_prompt = prompt_construction(EE_data)
        prompt = EE_data
        prompt['prompt_1'] = one_stage_prompt
        prompt['prompt_2'] = two_stage_prompt
        EE_prompt.append(prompt)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(EE_prompt, f, ensure_ascii=False, indent=2)