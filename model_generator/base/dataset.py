
import os
import json
from random import shuffle

class DataSet:
    def __init__(self):
        self.samples = []
    
    def add_from_folder(self, folder_path: str, 
                        label: str,
                        attr_from_name_index: int = None,
                        attr_from_name_separator: str = None,
                        ext: str = None):
        if ext is None:
            files = os.listdir(folder_path)
        else:
            files = [f for f in os.listdir(folder_path) if f.endswith(ext)]

        for f in files:
            if attr_from_name_index is not None and attr_from_name_separator is not None:
                try:
                    attr = f.split('.')[0].split(attr_from_name_separator)[attr_from_name_index]
                except Exception:
                    attr = None
            else: 
                attr = None
            self.samples.append({'file_path': os.path.join(folder_path, f),
                                 'label':label,
                                 'attr':attr})
                 
    def add_from_manifest(self, manifest_path: str, 
                          file_key,
                          label_key, 
                          attr_key = None, 
                          conditions: list = []):
        def process_keys(root, keys):
            res = root
            if type(keys) is list:
                for k in keys:
                    res = res[k]
                return res
            else:
                return root[keys]
            
        folder_path = os.path.dirname(manifest_path)
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        for sample in manifest:
            attr = process_keys(sample, attr_key) if attr_key is not None else None
            f = process_keys(sample, file_key)
            label = process_keys(sample, label_key)
            self.samples.append({'file_path': os.path.join(folder_path, f),
                                 'label':label.lower(),
                                 'attr':attr})

    def add_samples(self, samples):
        if hasattr(samples, '__iter__'):
            self.samples.extend(samples)
        else:
            self.samples.append(samples)
    
    def remove_duplicate(self):
        """ Check for duplicates and remove them.
        
        Returns
        =======
        n_duplicates (int) -- Number of removed duplicates
        """
        file_names = set()
        n_duplicate = 0
        for sample in self.samples:
            name = os.path.basename(sample['file_path'])
            if name not in file_names:
                file_names.add(name)
            else:
                self.samples.remove(sample)
                n_duplicate += 1
        return n_duplicate
        

    def get_subset_by_label(self, label:str):
        """ Returns a subset containing samples with given label. """
        subset = DataSet()
        subset.add_samples([sample for sample in self.samples if sample['label'] == (label.lower() if label is not None else None)])
        return subset
    
    def get_subset_by_labels(self, labels: list):
        """ Returns a subset containing samples with given labels. """
        subset = DataSet()
        subset.add_samples([sample for sample in self.samples if sample['label'] in [label.lower() if label is not None else None for label in labels]])
        return subset
        
    def split_dataset(self, ratios: list, split_using_attr: bool = False):
        """ Splits the dataset to len(ratios) subsets using ratio. """
        n_samples = len(self.samples)
        target_n_samples = list(reversed([round(r * (n_samples / sum(ratios))) for r in ratios]))
        delimiters = [sum(target_n_samples[:i]) for i in range(len(ratios))] + [n_samples]
        ret = list()
        if not split_using_attr:
            shuffle(self.samples)
        else:
            self.samples = sorted(self.samples, key=lambda x: x['attr'] if x['attr'] is not None else 'zzzz')
        for start, stop in zip(delimiters[:-1], delimiters[1:]):
            ds = DataSet()
            ds.add_samples(self.samples[start:stop])
            ret.append(ds) 
        return list(reversed(ret))

    def write(self, file_path: str):
        """ Write the dataset as a json file. """
        with open(file_path, 'w') as f:
            json.dump(self.samples, f)
    
    def load(self, json_file):
        """ Loads a dataset from a json file."""
        with open(json_file, 'r') as f:
            self.add_samples(json.load(f))

    def verify_and_clear(self):
        """ Returns sample that do not longer exist. """
        missing_samples = []
        for f in self.samples:
            if not os.path.isfile(f['file_path']):
                missing_samples.append(f)
                self.samples.remove(f)
        return missing_samples
        
    def clear(self):
        """ Empty the dataset"""
        self.samples = []


    def intersect(self, other):
        """ Return a dataset which is the intersection of the two input datasets """
        result = DataSet()
        file_names = set([os.path.basename(s['file_path']) for s in other.samples])
        for sample in self.samples:
            if os.path.basename(sample['file_path']) in file_names:
                result.add_samples(sample)

        return result

    def __add__(self, other):
        ret = DataSet()
        ret.add_samples(self.samples)
        ret.add_samples(other.sample) 
        return ret
    
    def __iadd__(self, other):
        self.add_samples(other.samples)
        return self
    
    def __isub__(self, other):
        """ Remove files from second set using file_path value """
        files_to_delete = [s['file_path'] for s in other.samples]
        for sample in self.samples:
            if sample['file_path'] in files_to_delete:
                self.samples.remove(sample)
        return self

    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, key):
        return self.samples[key]

    def __iter__(self):
        yield from self.samples

