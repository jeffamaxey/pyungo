import pytest
from pyungo.core import Graph, PyungoError


def test_simple():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    @graph.register(inputs=['d', 'a'], outputs=['e'])
    def f_my_function3(d, a):
        return d - a

    @graph.register(inputs=['c'], outputs=['d'])
    def f_my_function2(c):
        return c / 10.

    res = graph.calculate(data={'a': 2, 'b': 3})

    assert res == -1.5
    assert graph.data['e'] == -1.5


def test_simple_without_decorator():
    graph = Graph()

    def f_my_function(a, b):
        return a + b

    def f_my_function3(d, a):
        return d - a

    def f_my_function2(c):
        return c / 10.

    graph.add_node(f_my_function, inputs=['a', 'b'], outputs=['c'])
    graph.add_node(f_my_function3, inputs=['d', 'a'], outputs=['e'])
    graph.add_node(f_my_function2, inputs=['c'], outputs=['d'])

    res = graph.calculate(data={'a': 2, 'b': 3})

    assert res == -1.5
    assert graph.data['e'] == -1.5


def test_multiple_outputs():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c', 'd'])
    def f_my_function(a, b):
        return a + b, 2 * b

    @graph.register(inputs=['c', 'd'], outputs=['e'])
    def f_my_function2(c, d):
        return c + d

    res = graph.calculate(data={'a': 2, 'b': 3})

    assert res == 11
    assert graph.data['e'] == 11


def test_same_output_names():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    with pytest.raises(PyungoError) as err:
        @graph.register(inputs=['c'], outputs=['c'])
        def f_my_function2(c):
            return c / 10
    
    assert 'c output already exist' in str(err.value)


def test_missing_input():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    with pytest.raises(PyungoError) as err:
        graph.calculate(data={'a': 6})
    
    assert "The following inputs are needed: ['b']" in str(err.value)


def test_inputs_not_used():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    with pytest.raises(PyungoError) as err:
        graph.calculate(data={'a': 6, 'b': 4, 'e': 7})
    
    assert "The following inputs are not used by the model: ['e']" in str(err.value)


def test_inputs_collision():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    with pytest.raises(PyungoError) as err:
        graph.calculate(data={'a': 6, 'b': 4, 'c': 7})
    
    assert "The following inputs are already used in the model: ['c']" in str(err.value)


def test_circular_dependency():
    graph = Graph()

    @graph.register(inputs=['a', 'b', 'd'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    @graph.register(inputs=['c'], outputs=['d'])
    def f_my_function2(c):
        return c / 2.

    with pytest.raises(PyungoError) as err:
        graph.calculate(data={'a': 6, 'b': 4})
    
    assert "A cyclic dependency exists amongst" in str(err.value)


def test_iterable_on_single_output():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return list(range(a)) + [b]

    res = graph.calculate(data={'a': 2, 'b': 3})

    assert res == [0, 1, 3]
    assert graph.data['c'] == [0, 1, 3]


def test_multiple_outputs_with_iterable():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c', 'd'])
    def f_my_function(a, b):
        return list(range(a)) + [b], b * 10

    res = graph.calculate(data={'a': 2, 'b': 3})

    assert isinstance(res, tuple) is True
    assert graph.data['c'] == [0, 1, 3]
    assert graph.data['d'] == 30
    assert res[0] == [0, 1, 3]
    assert res[1] == 30


def test_args_kwargs():
    graph = Graph()

    @graph.register(
        inputs=['a', 'b'],
        args=['c'],
        kwargs=['d'],
        outputs=['e']
    )
    def f_my_function(a, b, *args, **kwargs):
        return a + b + args[0] + kwargs['d']

    res = graph.calculate(data={'a': 2, 'b': 3, 'c': 4, 'd': 5})

    assert res == 14
    assert graph.data['e'] == 14


def test_dag_pretty_print():
    graph = Graph()

    @graph.register(inputs=['a', 'b'], outputs=['c'])
    def f_my_function(a, b):
        return a + b

    @graph.register(inputs=['d', 'a'], outputs=['e'])
    def f_my_function3(d, a):
        return d - a

    @graph.register(inputs=['c'], outputs=['d'])
    def f_my_function2(c):
        return c / 10.

    expected = ['f_my_function', 'f_my_function2', 'f_my_function3']
    dag = graph.dag
    for i, fct_name in enumerate(expected):
        assert dag[i][0].fct_name == fct_name
