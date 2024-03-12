import json
import faiss
import numpy as np
import logging
import platform
sys_platform = platform.platform().lower()
logging.basicConfig(
    format="[demo_retriever:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s"
)
logging.getLogger().setLevel(logging.INFO)
class DemoRetriever(object):
    def __init__(self,demo_embs:np.array,demos:list,device:str='cpu'):
        """
        demo_embs: (n_demo, dim)
        demos: list of demos
        """

        self.demo_embs = demo_embs
        self.demos = demos
        assert len(self.demo_embs) == len(self.demos), 'demo_embs and demos should have the same length'
        # logging.info('Building index...')
        self.cpu_index_falt = faiss.IndexFlatL2(self.demo_embs.shape[1])
        if 'cuda' in device and 'windows' not in sys_platform:
            logging.info('Using GPU...')
            if device == 'cuda':
                logging.info('Multiple GPUs detected, using cuda:0')
                device = 'cuda:0'
            device_id = int(device.split(':')[-1])
            self.gpu_index_falt = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), device_id, self.cpu_index_falt)
        self.index_falt = self.gpu_index_falt if ('cuda' in device and 'windows' not in sys_platform) else self.cpu_index_falt
        self.index_falt.add(self.demo_embs)
        # logging.info('Done.')
        
    def retrieve(self,query_emb:np.array,topk:int=5)->list:
        """
        query_emb: (dim,)
        """
        D, I = self.index_falt.search(query_emb.reshape(1,-1), topk) 
        # retrieve demos
        retrieved_demos = [self.demos[i] for i in I[0]]
        
        return retrieved_demos
    
    def retrieve_with_filtering(self,target_type_set:set,universal_map:dict,query_emb:np.array,topk:int=5)->list:
        # retrieve demos more than topk*100
        retrieved_demos = self.retrieve(query_emb,topk*100)
        filter_result = []
        for demo in retrieved_demos:
            # get entity types
            entities_set = set([universal_map[entity['type']] for entity in demo['entities']])
            # if entities_set is a subset of target_type_set
            if entities_set.issubset(target_type_set):
                filter_result.append(demo)
        
        return filter_result[:topk]