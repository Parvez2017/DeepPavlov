"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, softwaredata
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path
import copy

import numpy as np
from sklearn.model_selection import train_test_split

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.dataset import Dataset
from deeppavlov.core.common import paths
from deeppavlov.models.preprocessors.preprocessors import PREPROCESSORS


@register('classification_dataset')
class ClassificationDataset(Dataset):
    def __init__(self, data, seed=None,
                 fields_to_merge=None, merged_field=None,
                 field_to_split=None, split_fields=None, split_proportions=None,
                 prep_method_name: str = None,
                 *args, **kwargs):

        super().__init__(data, seed)

        if fields_to_merge is not None:
            if merged_field is not None:
                print("Merging fields <<{}>> to new field <<{}>>".format(fields_to_merge,
                                                                         merged_field))
                self._merge_data(fields_to_merge=fields_to_merge,
                                 merged_field=merged_field)
            else:
                raise IOError("Given fields to merge BUT not given name of merged field")

        if field_to_split is not None:
            if split_fields is not None:
                print("Splitting field <<{}>> to new fields <<{}>>".format(field_to_split,
                                                                           split_fields))
                self._split_data(field_to_split=field_to_split,
                                 split_fields=split_fields,
                                 split_proportions=[float(s) for s in
                                                    split_proportions])
            else:
                raise IOError("Given field to split BUT not given names of split fields")

        self.prep_method_name = prep_method_name

        if prep_method_name:
            self.data = self.preprocess(PREPROCESSORS[prep_method_name])

    def _split_data(self, field_to_split, split_fields, split_proportions):
        data_to_div = self.data[field_to_split].copy()
        data_size = len(self.data[field_to_split])
        for i in range(len(split_fields) - 1):
            self.data[split_fields[i]], \
            data_to_div = train_test_split(data_to_div,
                                           test_size=
                                           len(data_to_div) - int(
                                               data_size * split_proportions[i]))
        self.data[split_fields[-1]] = data_to_div
        return True

    def _merge_data(self, fields_to_merge, merged_field):
        data = self.data.copy()
        data[merged_field] = []
        for name in fields_to_merge:
            data[merged_field] += self.data[name]
        self.data = data
        return True

    def preprocess(self, prep_method):

        data_copy = copy.deepcopy(self.data)

        for data_type in self.data:
            chunk = self.data[data_type]
            for i, sample in enumerate(chunk):
                data_copy[i] = (prep_method([sample[0]])[0], chunk[i][1])
        return data_copy



