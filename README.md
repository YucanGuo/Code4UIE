# Code4UIE

This is the official code release of the following paper:

Retrieval-Augmented Code Generation for Universal Information Extraction

## Usage

### Environment Setup

```
conda create -n Code4UIE python=3.10

activate Code4UIE

pip install -r requirements.txt
```

### Dataset Preparation

Please generate and put the dataset files to `[task]/[dataset]`, including `train.json` and `test.json`. (Dataset files will not be provided in this repo due to copyright concerns.)

There is an example of the data format in those JSON files:

```
[
  {
    "event_mentions": [
      {
        "event_type": "Phishing",
        "trigger": {
          "text": "Phishing",
          "start": 0,
          "end": 1
        },
        "arguments": [],
        "code": "phishing_event1 = Phishing(\n    trigger = Trigger(\"Phishing\"),\n)"
      },
      {
        "event_type": "Databreach",
        "trigger": {
          "text": "health data breaches",
          "start": 12,
          "end": 15
        },
        "arguments": [
          {
            "text": "UConn Health",
            "role": "victim",
            "type": "Organization",
            "start": 19,
            "end": 21
          },
          {
            "text": "326,000",
            "role": "number_of_victim",
            "type": "Number",
            "start": 23,
            "end": 24
          },
          {
            "text": "individuals",
            "role": "victim",
            "type": "Person",
            "start": 24,
            "end": 25
          }
        ],
        "code": "databreach_event1 = Databreach(\n    trigger = Trigger(\"health data breaches\"),\n    victim = [\n        Entity(\"UConn Health\"),\n        Entity(\"individuals\"),\n    ],\n    number_of_victim = [\n        Entity(\"326,000\"),\n    ],\n)"
      }
    ],
    "code_1": "phishing_event1 = Phishing(\n    trigger = Trigger(\"Phishing\"),\n)\ndatabreach_event1 = Databreach(\n    trigger = Trigger(\"health data breaches\"),\n    victim = [\n        Entity(\"UConn Health\"),\n        Entity(\"individuals\"),\n    ],\n    number_of_victim = [\n        Entity(\"326,000\"),\n    ],\n)",
    "code_2": "from Event import Databreach,Phishing",
    "sentence": "Phishing and other hacking incidents have led to several recently reported large health data breaches , including one that UConn Health reports affected 326,000 individuals ."
  },
...
]
```

where `"code_1"` contains the standard output of stage 2, and `"code_2"` contains the standard output of stage 1.

### Retrieval File Preparation

1. Please download the retrieval-related models from `https://huggingface.co/sentence-transformers/all-mpnet-base-v2` and `https://huggingface.co/flair/ner-english-ontonotes-large`, and put them to the folder `retrieval_models`.
2. Please install the retrieval-related package: `conda install -c pytorch faiss-gpu` (Linux) or `conda install -c pytorch faiss-cpu` (Windows).
3. Then, run `python get_dataset_embed.py` to generate retrieval files. Note that variables `dataset_name_list` and `datapath` in lines 16 and 18 should be changed according to the task and datasets.

### Prompt Construction

Run `python [task]_Prompt.py` to construct prompts for each task accordingly.

Necessary arguments are:

* `dataset`: Name of the dataset.
* `test_file`: File path of the test set.
* `train_file`: File path of the train set.
* `retrieval_strategy`: Retrieval strategy, including `'random'`, `'sentence_emb'`, and `'anonymized_sentence_emb'`.
* `output_file`: The output file path.
* `incontext_examples_num`: The number of in-context examples.

### Information Extraction

Run `python get_extraction_result.py` to interact with LLMs and get extraction results. Note that the value of variable `openai.api_key` in line 6 should be filled.

Necessary arguments are:

* `model`: Name of the dataset.
* `task`: Name of the task, including `'NER'`, `'RE'`, `'EAE'` and `'EE'`.
* `dataset`: Name of the dataset.
* `prompt_type`: Type of the prompt, including `'1stage'`, `'2stage'`, and `'1&2stage'`.
* `input_file`: The input file path.
* `output_file`: The output file path.
