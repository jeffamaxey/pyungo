""" class abstracting data passed as inputs and saved as outputs """
from copy import deepcopy

from .errors import PyungoError


class Data:
    def __init__(self, inputs, do_deepcopy=True):
        self._inputs = deepcopy(inputs) if do_deepcopy else inputs
        self._outputs = {}

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def __getitem__(self, key):
        try:
            return self._inputs[key]
        except KeyError:
            return self._outputs[key]

    def __setitem__(self, key, val):
        self._outputs[key] = val

    def check_inputs(self, sim_inputs, sim_outputs, sim_kwargs):
        """ make sure data inputs provided are good enough """
        data_inputs = set(self.inputs.keys())
        if diff := data_inputs - (data_inputs - set(sim_outputs)):
            msg = "The following inputs are already used in the model: {}"
            raise PyungoError(msg.format(list(diff)))
        inputs_to_provide = set(sim_inputs) - set(sim_outputs)
        if diff := inputs_to_provide - data_inputs:
            msg = f"The following inputs are needed: {list(diff)}"
            raise PyungoError(msg)
        if diff := data_inputs - inputs_to_provide - set(sim_kwargs):
            msg = "The following inputs are not used by the model: {}"
            raise PyungoError(msg.format(list(diff)))
