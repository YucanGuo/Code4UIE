#-*- coding:Utf-8 -*-
import openai
import json
import argparse

openai.api_key = '' # TODO: add your openai api key here
openai_model = 'gpt-3.5-turbo' #"gpt-3.5-turbo-16k"
input_file, output_file, prompt_type = '', '', ''

def chat_req(system_role, prompt):
    rsp = openai.ChatCompletion.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature = 0.0,
        stop=["\"\"\"", "#"]
    )
    ans = rsp['choices'][0]['message']['content'].strip()
    return ans

def openai_req(prompt):
    rsp = openai.Completion.create(
        model=openai_model,
        prompt=prompt,
        temperature=0.0,
        max_tokens=128,
        top_p=1,
        n=1,
        logprobs=None,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\"\"\"", "#"]
        )
    ans = rsp['choices'][0]['text'].strip()
    return ans

def get_NER_result():
    #one-stage role definition
    system_role = 'You are a highly intelligent and accurate named-entity recognition model and Python coder. You take a sentence as input and convert it into named entities as instances of a set of predefined Python classes.\n'
    #two-stage role definitions
    system_role_1 = 'You are a highly intelligent and accurate named-entity recognition model and Python coder. You take a sentence as input and convert it into types of named entity as an import statement of Python.\n'
    system_role_2 = 'You are a highly intelligent and accurate named-entity recognition model and Python coder. You take a sentence as input and convert it into named entities as instances of a set of predefined Python classes.\n'
    with open(input_file,'r',encoding='utf-8') as f:
        NER_inputs = json.load(f)
    NER_results = []
    for NER_input in NER_inputs:
        NER_result = NER_input
        prompt_NER = NER_input['prompt_1']
        #one-stage prompt
        if prompt_type in ['1stage', '1&2stage']:
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role, prompt_NER)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_NER)
            prediction_NER = rsp
            NER_result['prediction_NER'] = prediction_NER
        else:
            NER_result['prediction_NER'] = ''
        #two-stage prompt
        if prompt_type in ['2stage', '1&2stage']:
            #stage 1
            prompt_s1 = NER_input['prompt_2']['stage_1']
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role_1, prompt_s1)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_s1)
            if 'None' in rsp:
                NER_result['prediction_s1'], NER_result['prediction_s2'] = 'None', 'None'
                NER_results.append(NER_result)
                with open(output_file,'w',encoding='utf-8') as f:
                    json.dump(NER_results, f, ensure_ascii=False, indent=2)
                continue
            prediction_s1 = 'from Entity import ' + rsp
            NER_result['prediction_s1'] = prediction_s1
            entity_defs = json.load(open(args.task + '/' + args.dataset +'/class_defs_json/Entity.json', encoding='utf-8'))
            entity_types = set()
            for entity_type in rsp.split(','):
                entity_type = entity_type.strip(' ')
                if entity_type in entity_defs.keys():
                    entity_types.add(entity_type)
            #stage 2
            prompt_s2 = NER_input['prompt_2']['stage_2'][0]
            for entity_type in entity_types:
                prompt_s2 += entity_defs[entity_type] + '\n'
            prompt_s2 += NER_input['prompt_2']['stage_2'][1]
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role_2, prompt_s2)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_s2)
            prediction_s2 = rsp
            NER_result['prediction_s2'] = prediction_s2
        else:
            NER_result['prediction_s1'], NER_result['prediction_s2'] = '', ''
        NER_results.append(NER_result)
        with open(output_file,'w',encoding='utf-8') as f:
            json.dump(NER_results, f, ensure_ascii=False, indent=2)
    return

def get_RE_result():
    #one-stage role definition
    system_role = 'You are a highly intelligent and accurate relation extraction model and Python coder. You take a sentence as input and convert it into relations as instances of a set of predefined Python classes.\n'
    #two-stage role definitions
    system_role_1 = 'You are a highly intelligent and accurate relation extraction model and Python coder. You take a sentence as input and convert it into relation types as an import statement of Python.'
    system_role_2 = 'You are a highly intelligent and accurate relation extraction model and Python coder. You take a sentence as input and convert it into relations as instances of a set of predefined Python classes.\n'
    with open(input_file,'r',encoding='utf-8') as f:
        RE_inputs = json.load(f)
    RE_results = []
    for RE_input in RE_inputs:
        RE_result = RE_input
        prompt_RE = RE_input['prompt_1']
        #one-stage prompt
        if prompt_type in ['1stage', '1&2stage']:
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role, prompt_RE)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_RE)
            prediction_RE = rsp
            RE_result['prediction_RE'] = prediction_RE
        else:
            RE_result['prediction_RE'] = ''
        #two-stage prompt
        if prompt_type in ['2stage', '1&2stage']:
            #stage 1
            prompt_s1 = RE_input['prompt_2']['stage_1']
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role_1, prompt_s1)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_s1)
            prediction_s1 = 'from Relation import ' + rsp
            RE_result['prediction_s1'] = prediction_s1
            entity_defs = json.load(open(args.task + '/' + args.dataset + '/class_defs_json/Entity.json'))
            relation_defs = json.load(open(args.task + '/' + args.dataset + '/class_defs_json/Relation.json'))
            relation_types = set()
            for relation_type in rsp.split(','):
                relation_type = relation_type.strip(' ')
                if relation_type in relation_defs.keys():
                    relation_types.add(relation_type)
            #stage 2
            prompt_s2 = RE_input['prompt_2']['stage_2'][0]
            #definitions of entities be imported
            entities = set()
            for relation_type in relation_types:
                relation_def = relation_defs[relation_type]
                entity_lists = relation_def.split(' = "",')[0:2]
                for entity_list in entity_lists:
                    entity_list = entity_list.split(': ')[1]
                    entity_list = entity_list.split('|')
                    for entity in entity_list:
                        entity = entity.strip(' ')
                        entities.add(entity)
            for entity in entities:
                prompt_s2 += entity_defs[entity] + '\n'
            for relation_type in relation_types:
                prompt_s2 += relation_defs[relation_type] + '\n'
            prompt_s2 += RE_input['prompt_2']['stage_2'][1]
            if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
                rsp = chat_req(system_role_2, prompt_s2)
            if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
                rsp = openai_req(prompt_s2)
            prediction_s2 = rsp
            RE_result['prediction_s2'] = prediction_s2
        else:
            RE_result['prediction_s1'], RE_result['prediction_s2'] = '', ''
        RE_results.append(RE_result)
        with open(output_file,'w',encoding='utf-8') as f:
            json.dump(RE_results, f, ensure_ascii=False, indent=2)
    return

def get_EE_result():
    system_role_ED = 'You are a highly intelligent and accurate event detection model and Python coder. You take a sentence as input and convert it into event types as an import statement of Python.\n'
    with open(input_file,'r',encoding='utf-8') as f:
        EE_inputs = json.load(f)
    EE_results = []
    if args.dataset == 'ACE05':
        entity_defs = json.load(open(args.task + '/' + args.dataset + '/class_defs_json/Entity.json'))
    event_defs = json.load(open(args.task + '/' + args.dataset + '/class_defs_json/Event.json'))
    for EE_input in EE_inputs:
        EE_result = EE_input
        prompt_ED = 'from typing import List\n\n' + EE_input['prompt_2']['stage_1']
        if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
            rsp = chat_req(system_role_ED, prompt_ED)
        if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
            rsp = openai_req(prompt_ED)
        if(rsp == 'None'): #empty sentence
            EE_result['prediction_ED'] = 'None'
            EE_result['prediction_EAE'] = 'None'
            EE_results.append(EE_result)
            with open(output_file,'w',encoding='utf-8') as f:
                json.dump(EE_results, f, ensure_ascii=False, indent=2)
            continue
        prediction_ED = 'from Event import ' + rsp
        EE_result['prediction_ED'] = prediction_ED
        event_types = set()
        for event_type in rsp.split(','):
            event_type = event_type.strip(' ')
            if event_type in event_defs.keys():
                event_types.add(event_type)

        prompt_EAE = 'from typing import List\n\n' + EE_input['prompt_2']['stage_2'][0]
        #definitions of entities be imported
        if args.dataset in ['ACE05']:
            entities = set()
            for event_type in event_types:
                event_def = event_defs[event_type]
                entity_lists = event_def.split('List')[1:]
                for entity_list in entity_lists:
                    entity_list = entity_list.split(']')[0].strip('[')
                    entity_list = entity_list.split('|')
                    for entity in entity_list:
                        entity = entity.strip(' ')
                        entities.add(entity)
            for entity in entities:
                prompt_EAE += entity_defs[entity] + '\n\n'
        #definitions of events be imported
        for event_type in event_types:
            prompt_EAE += event_defs[event_type] + '\n\n'
        prompt_EAE += EE_input['prompt_2']['stage_2'][1]
        system_role_EAE = 'You are a highly intelligent and accurate event argument extraction model and Python coder. You take a sentence as input and convert it into events arguments as instances of a set of predefined Python classes.\n'
        if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
            rsp = chat_req(system_role_EAE, prompt_EAE)
        if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
            rsp = openai_req(prompt_EAE)
        prediction_EAE = rsp
        EE_result['prediction_EAE'] = prediction_EAE
        EE_results.append(EE_result)
        with open(output_file,'w',encoding='utf-8') as f:
            json.dump(EE_results, f, ensure_ascii=False, indent=2)
    return

def get_EAE_result():
    system_role = 'You are a highly intelligent and accurate event argument extraction model and Python coder. You take a sentence as input and convert it into event arguments as an instance of a predefined Python class.\n'
    with open(input_file,'r',encoding='utf-8') as f:
        EAE_inputs = json.load(f)
    EAE_results = []
    for EAE_input in EAE_inputs:
        EAE_result = EAE_input
        prompt = EAE_input['prompt']
        if openai_model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k']:
            rsp = chat_req(system_role, prompt)
        if openai_model in ['code-davinci-002', 'text-davinci-002', 'text-davinci-003']:
            rsp = openai_req(prompt)
        prediction = prompt.split('\"\"\"\n')[-1] + '\n    ' + rsp
        EAE_result['prediction'] = prediction
        EAE_results.append(EAE_result)
    with open(output_file,'w',encoding='utf-8') as f:
        json.dump(EAE_results, f, ensure_ascii=False, indent=2)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='code-davinci-002', choices=['text-davinci-002', 'code-davinci-002', 'text-davinci-003', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'])
    parser.add_argument('--task', type=str, default='RE', choices=['NER', 'RE', 'EE', 'EAE'])
    parser.add_argument('--dataset', type=str, default='NYT')
    parser.add_argument('--prompt_type', type=str, default='2stage', choices=['1stage', '2stage', '1&2stage'])
    parser.add_argument('--input_file', type=str, default='RE/NYT/prompt/RE-nyt-1&2stage-code-ase-15.json')
    parser.add_argument('--output_file', type=str, default='RE/NYT/output/RE-davinci2-nyt-2stage-code-ase-15.json') 
    args = parser.parse_args()
    openai_model = args.model
    input_file = args.input_file
    output_file = args.output_file
    prompt_type = args.prompt_type
    if args.task == 'NER':
        get_NER_result()
    if args.task == 'RE':
        get_RE_result()
    if args.task == 'EE':
        get_EE_result()
    if args.task == 'EAE':
        get_EAE_result()