'''
[Base Class Definition of Entity and Event]
[Definitions of Entities be Imported]
[Definition of Event be Imported]
{In-context Examples}
"""
Translate the following sentence into an instance of the Event subclass [event_type].
"{sentence}" 
"""
[event_type]_event = [event_type](
    trigger = [trigger]
'''
import json
from demo_retriever import demo_retriever
import random
import argparse
incontext_examples_num = 10
incontext_examples_dir = ''

def add_incontext_examples(sentence:str, event_type: str, num: int):
    prompt = ''
    if args.retrieval_strategy == 'random':
        examples = []
        incontext_examples = []
        parent_cls_name, cur_cls_name = event_type.split(':')
        with open(incontext_examples_dir, 'r', encoding='utf-8') as f:
            events = json.load(f)
        for event in events:
            tmp_parent_cls_name = event['event_type'].split(':')[0]
            if tmp_parent_cls_name == parent_cls_name:
                examples.append(event)
        incontext_examples = random.sample(examples, num)
    else:
        incontext_examples = demo_retriever(sentence, 'EAE', args.dataset, args.retrieval_strategy, args.incontext_examples_num)
    for example in incontext_examples:
        prompt += '"""\nTranslate the following sentence into an instance of the Event subclass {}. The trigger word(s) of the event is marked with **trigger word**.\n\"{}\"\n"""'.format(example['event_type'], example['sentence']) + '\n'
        prompt += example['code'] + '\n\n'
    return prompt

def prompt_construction(event: dict):
    prompt = ''
    base_class_defs = json.load(open('EAE/' + args.dataset + '/class_defs_json/Base_Class.json'))
    entity_defs = json.load(open('EAE/' + args.dataset + '/class_defs_json/Entity.json'))
    event_defs = json.load(open('EAE/' + args.dataset + '/class_defs_json/Event.json'))
    prompt += base_class_defs['Entity'] + '\n\n' + base_class_defs['Event'] + '\n\n'
    event_type = event['event_type'].split(':')[1].replace('-', '_')
    event_def = event_defs[event_type]
    entities = set()
    entity_lists = event_def.split('List')[1:]
    for entity_list in entity_lists:
        entity_list = entity_list.split(']')[0].strip('[')
        entity_list = entity_list.split('|')
        for entity in entity_list:
            entity = entity.strip(' ')
            entities.add(entity)
    for entity in entities:
        prompt += entity_defs[entity] + '\n\n'
    prompt += event_defs['Trigger'] + '\n\n' + event_def + '\n\n'
    prompt += add_incontext_examples(event['sentence'], event['event_type'], incontext_examples_num)
    prompt += '"""\nTranslate the following sentence into an instance of the Event subclass {}. The trigger word(s) of the event is marked with **trigger word**.\n\"{}\"\n"""'.format(event_type, event['sentence']) + '\n'
    prompt += event['code'].split(',')[0] + ','
    return prompt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='ACE05')
    parser.add_argument('--test_file', type=str, default='EAE/ACE05/test.json')
    parser.add_argument('--train_file', type=str, default='EAE/ACE05/train.json')
    parser.add_argument('--retrieval_strategy', type=str, default='entity_only_emb', choices=['random', 'sentence_emb', 'anonymized_sentence_emb'])
    parser.add_argument('--output_file', type=str, default='EAE/ACE05/prompt/EAE-ace05-1stage-codev1-eoe-10.json')
    parser.add_argument('--incontext_examples_num', type=int, default=10)
    args = parser.parse_args()
    incontext_examples_num = args.incontext_examples_num
    incontext_examples_dir = args.train_file
    with open(args.test_file, 'r', encoding='utf-8') as f:
        events = json.load(f)
    events_prompt = []
    for event in events:    
        prompt = prompt_construction(event)
        event_prompt = event
        event_prompt['prompt'] = prompt
        events_prompt.append(event_prompt)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(events_prompt, f, ensure_ascii=False, indent=2)