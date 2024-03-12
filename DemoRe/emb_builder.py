from transformers import AutoModel, AutoTokenizer
import torch
from .utilities.embs_utils import mean_pooling
import logging
logging.basicConfig(
    format="[emb_builder:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
)
logging.getLogger().setLevel(logging.INFO)
class EmbeddingBuilder():
    def __init__(self, model_name):
        logging.info('Loading model: %s'%model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        logging.info('Done.')
        
    def get_word_embeddings(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        return model_output[0]
    
    def get_cls_origin_embedding(self, text):
        word_embeddings = self.get_word_embeddings(text)
        cls_token = word_embeddings[:, 0, :]
        return cls_token

    def get_cls_pooler_embedding(self, text):
        """
        cls_pooler is the based on the 
        https://github.com/huggingface/transformers/blob/fded6f41861561a1e3311850e5d11c4bbf8a0fb3/src/transformers/models/bert/modeling_bert.py#L654
        namely, the first token embedding (like [CLS]) is used to do linear transformation
        """
        encoded_input = self.tokenizer(text, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        return model_output[1]
    
    def get_mean_pooling_embedding(self, text):
        """
        get_mean_pooling_embedding
        mean_pooling is the mean of all word embeddings,
        """
        encoded_input = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        return mean_pooling(model_output, encoded_input['attention_mask'])
    

if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')


    test_sentence = "Hello, my dog is cute"

    encoded_input = tokenizer(test_sentence, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)