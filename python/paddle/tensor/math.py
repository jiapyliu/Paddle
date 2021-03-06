#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
math functions
"""

from __future__ import print_function

from paddle.common_ops_import import *
from ..fluid import layers
from ..fluid.framework import core
from ..fluid.layers.layer_function_generator import _generate_doc_string_

# TODO: define math functions
# yapf: disable
__all__ = [
#            'abs',
#            'acos',
#            'asin',
           'atan',
#            'ceil',
#            'cos',
#            'cumsum',
#            'elementwise_add',
#            'elementwise_div',
#            'elementwise_floordiv',
#            'elementwise_max',
#            'elementwise_min',
#            'elementwise_mod',
#            'elementwise_mul',
#            'elementwise_pow',
#            'elementwise_sub',
#            'exp',
#            'floor',
#            'increment',
#            'log',
           'mul',
#            'multiplex',
           'pow',
#            'reciprocal',
#            'reduce_max',
#            'reduce_min',
#            'reduce_prod',
#            'reduce_sum',
#            'round',
#            'rsqrt',
#            'scale',
#            'sign',
           'sin',
           'sqrt',
#            'square',
#            'stanh',
           'sum',
#            'sums',
           'tanh',
           'elementwise_sum',
#            'max',
#            'min',
           'mm',
           'div',
           'add',
#            'atan',
           'logsumexp',
#            'inverse',
#            'log1p',
#            'erf',
#            'addcmul',
           'addmm'
]
# yapf: enable.


def generate_op_noattr(op_type):
    """Register the Python layer for an Operator without Attribute..

    Args:
       op_type: The name of the operator to be created.

    This function takes in the operator type (sin, tanh etc) and
    creates the operator functionality.

    """
    op_proto = OpProtoHolder.instance().get_op_proto(op_type)

    def func(x, name=None, out=None):
        if in_dygraph_mode():
            op = getattr(core.ops, op_type)
            return op(x)

        check_variable_and_dtype(x, 'x', ['float16', 'float32', 'float64'],
                                 op_type)
        helper = LayerHelper(op_type, **locals())

        if name and out:
            warnings.warn(
                "Both name and out parameters have been set in fluid.tensor.math.%s(), only out will take effect to specify the result storage. "
                "You can discard either one to solve this warning." % op_type,
                category=UserWarning,
                stacklevel=2)
        if not out:
            out = helper.create_variable_for_type_inference(dtype=x.dtype)
        helper.append_op(type=op_type, inputs={"X": x}, outputs={"Out": out})
        return out

    func.__name__ = op_type
    func.__doc__ = _generate_doc_string_(
        op_proto,
        additional_args_lines=[
            "name(str, optional): The default value is None.  Normally there is no need for user to set this property.  For more information, please refer to :ref:`api_guide_Name`.\n    "
            "out(Variable, optional): The default value is None. Optional output can be any created Variable that meets the requirements to store the result of operation. if out is None, a new Varibale will be create to store the result."
        ])
    func.__doc__ = func.__doc__ + """

Return type
  Variable
Examples:
    .. code-block:: python

        import numpy as np
        
        import paddle
        import paddle.fluid as fluid

        inputs = fluid.data(name="x", shape = [None, 4], dtype='float32')
        output = paddle.%s(inputs)

        exe = fluid.Executor(fluid.CPUPlace())
        exe.run(fluid.default_startup_program())

        #input.shape=1X4, batch_size=1
        img = np.array([[1.0, 2.0, 3.0, 4.0]]).astype(np.float32)
        res = exe.run(fluid.default_main_program(), feed={'x':img}, fetch_list=[output])
        print(res)
""" % op_type
    return func

@templatedoc()
def pow(input, exponent, out=None, name=None):
    """
    This is Pow Activation Operator.

    :math:`out = input^{exponent}`

    Args:
        input(Variable): A ``Tensor`` or ``LoDTensor`` . The data type is ``float32`` or ``float64``.
        exponent(float32|Variable): A scalar with type ``float32`` or a ``Tensor`` with shape [1] and type ``float32``.
        out (Variable, optional):  The Variable that stores results of the operation. 
            If out is None, a new Variable will be created to store the results.
        name(str, optional): The default value is None. Normally there is no need for user to set this property. 
            For more information, please refer to :ref:`api_guide_Name` .

    Returns:
        Variable: A ``Tensor`` or ``LoDTensor``. The data type is same as ``input``.

    Examples:

        .. code-block:: python

            import paddle
            import paddle.fluid as fluid

            x = fluid.data(name="x", shape=[32,32], dtype="float32")

            # example 1: argument exponent is float
            res = fluid.data(name="output", shape=[32,32], dtype="float32")
            y_1 = paddle.pow(x, 2.0, out=res)
            # y_1 is x^{2.0}

            # example 2: argument exponent is Variable
            exponet_tensor = fluid.layers.fill_constant([1], "float32", 3.0)
            res = fluid.data(name="output", shape=[32,32], dtype="float32")
            y_2 = paddle.pow(x, exponet_tensor, out=res)
            # y_2 is x^{3.0}
    """
    helper = LayerHelper('pow', **locals())
    inputs = {'X': input}
    attrs = {}
    if isinstance(exponent, Variable):
        exponent.stop_gradient = True
        inputs['FactorTensor'] = exponent
    else:
        attrs['factor'] = exponent

    if out is None:
        out = helper.create_variable_for_type_inference(dtype=input.dtype)
    else:
        check_dtype(
            out.dtype, out.name,
            convert_dtype(input.dtype), 'pow',
            '(The out data type in pow must be the same with input data type.)')
        if name:
            warnings.warn(
                "The output Variable name of the paddle.tensor.pow operation can only be given by parameter out or name. \
                When parameter out and name are set at the same time, out has a higher priority than name. \
                Finally, the output Variable name is same as the out name %s"
                                                                              %
                out.name,
                category=UserWarning,
                stacklevel=2)

    helper.append_op(
        type='pow', inputs=inputs, outputs={'Out': out}, attrs=attrs)
    return out


def mul(x, y, x_num_col_dims=1, y_num_col_dims=1, out=None, name=None):
    """
    Mul Operator.
    This operator is used to perform matrix multiplication for input $x$ and $y$.
    The equation is:

    ..  math::
        Out = x * y

    Both the input $x$ and $y$ can carry the LoD (Level of Details) information, or not. 
    But the output only shares the LoD information with input $x$.

    Args:
        x (Variable): The first input Tensor/LoDTensor of mul_op.
        y (Variable): The second input Tensor/LoDTensor of mul_op.
        x_num_col_dims (int, optional): The mul_op can take tensors with more than two dimensions as its inputs. 
            If the input $x$ is a tensor with more than two dimensions, $x$ will be flattened into a two-dimensional 
            matrix first. The flattening rule is: the first `num_col_dims` will be flattened to form the first 
            dimension of the final matrix (the height of the matrix), and the rest `rank(x) - num_col_dims` 
            dimensions are flattened to form the second dimension of the final matrix (the width of the matrix). 
            As a result, height of the flattened matrix is equal to the product of $x$'s first `x_num_col_dims` dimensions' 
            sizes, and width of the flattened matrix is equal to the product of $x$'s last `rank(x) - num_col_dims` 
            dimensions' size. For example, suppose $x$ is a 6-dimensional tensor with the shape [2, 3, 4, 5, 6], 
            and `x_num_col_dims` = 3. Thus, the flattened matrix will have a shape [2 x 3 x 4, 5 x 6] = [24, 30]. Default is 1. 
        y_num_col_dims (int, optional): The mul_op can take tensors with more than two dimensions as its inputs. If the 
            input $y$ is a tensor with more than two dimensions, $y$ will be flattened into a two-dimensional matrix first. 
            The attribute `y_num_col_dims` determines how $y$ is flattened. See comments of `x_num_col_dims` for more details. 
            Default is 1. 
        out(Variable, optinal): The Variable that stores results of the operation. If out is None, 
            a new Variable will be created to store the results.
        name (str, optional): Name of the output. Normally there is no need for user to set this property. 
            For more information, please refer to :ref:`api_guide_Name`. Default is None. If both of out and name are not None, 
            the output name will be same as out. 

    Returns:
        Variable(Tensor/LoDTensor): The output Tensor/LoDTensor of mul op.

    Examples:
        ..  code-block:: python
            
            import paddle
            import paddle.fluid as fluid
            dataX = fluid.data(name="dataX", shape=[2, 5], dtype="float32")
            dataY = fluid.data(name="dataY", shape=[5, 3], dtype="float32")
            
            res = fluid.data(name="output", shape=[2, 3], dtype="float32")
            output = paddle.mul(dataX, dataY,
                                      x_num_col_dims = 1,
                                      y_num_col_dims = 1, 
                                      out=res)
            

    """
    inputs = {"X": [x], "Y": [y]}
    attrs = {"x_num_col_dims": x_num_col_dims, "y_num_col_dims": y_num_col_dims}
    if in_dygraph_mode():
        outs = core.ops.mul(inputs, attrs)
        return outs['Out'][0]

    helper = LayerHelper("mul", **locals())
    check_variable_and_dtype(x, 'x', ['float16', 'float32', 'float64'], 'mul')
    check_variable_and_dtype(y, 'y', ['float16', 'float32', 'float64'], 'mul')

    if out is None:
        out = helper.create_variable_for_type_inference(dtype=x.dtype)
    else:
        check_dtype(
            out.dtype, out.name,
            convert_dtype(x.dtype), 'mul',
            '(The out data type in pow must be the same with input data type.)')
        if name:
            warnings.warn(
                "The output Variable name of the paddle.tensor.pow operation can only be given by parameter out or name.\
                When parameter out and name are set at the same time, out has a higher priority than name. \
                Finally, the output Variable name is same as the out name %s"
                                                                              %
                out.name,
                category=UserWarning,
                stacklevel=2)
    helper.append_op(
        type="mul", inputs={"X": x,
                            "Y": y}, attrs=attrs, outputs={"Out": out})
    return out


__ops__noattr__ = [
    'atan',
    'sin',
    'sqrt',
    'tanh',
]

for _OP in set(__ops__noattr__):
    globals()[_OP] = generate_op_noattr(_OP)


@dygraph_only
def _elementwise_op_in_dygraph(x,
                               y,
                               axis=-1,
                               act=None,
                               use_mkldnn=False,
                               op_name=None):
    op = getattr(core.ops, op_name)
    out = op(x, y, 'axis', axis, 'use_mkldnn', use_mkldnn)

    return dygraph_utils._append_activation_in_dygraph(
        out, act, use_mkldnn=use_mkldnn)


def _elementwise_op(helper):
    op_type = helper.layer_type
    original_op_type = helper.kwargs.get('original_op_type', op_type)
    x = helper.kwargs.get('x', None)
    y = helper.kwargs.get('y', None)

    assert x is not None, 'x cannot be None in {}'.format(original_op_type)
    assert y is not None, 'y cannot be None in {}'.format(original_op_type)
    check_variable_and_dtype(
        x, 'x', ['float16', 'float32', 'float64', 'int32', 'int64'],
        original_op_type)
    check_variable_and_dtype(
        y, 'y', ['float16', 'float32', 'float64', 'int32', 'int64'],
        original_op_type)

    axis = helper.kwargs.get('axis', -1)
    use_mkldnn = helper.kwargs.get('use_mkldnn', False)
    name = helper.kwargs.get('name', None)
    out = helper.kwargs.get('out', None)
    if out is None:
        if name is None:
            out = helper.create_variable_for_type_inference(dtype=x.dtype)
        else:
            out = helper.create_variable(
                name=name, dtype=x.dtype, persistable=False)

    helper.append_op(
        type=op_type,
        inputs={'X': x,
                'Y': y},
        outputs={'Out': out},
        attrs={'axis': axis,
               'use_mkldnn': use_mkldnn})
    return helper.append_activation(out)


def add(x, y, alpha=1, out=None, name=None):
    """
Examples:

    .. code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.array([2, 3, 4]).astype('float32'),
                "y": np.array([1, 5, 2]).astype('float32')
            }

        x = fluid.data(name="x", shape=[3], dtype='float32')
        y = fluid.data(name="y", shape=[3], dtype='float32')
        z1 = paddle.add(x, y)
        z2 = paddle.add(x, y, alpha=10)
        # z = x + y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)
        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z1.name, z2.name])

        print(z_value[0]) # [3., 8., 6.]
        print(z_value[1]) # [12. 53. 24.]


    .. code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.ones((2, 3, 4, 5)).astype('float32'),
                "y": np.zeros((4, 5)).astype('float32')
            }

        x = fluid.data(name="x", shape=[2, 3, 4, 5], dtype='float32')
        y = fluid.data(name="y", shape=[4, 5], dtype='float32')
        z = paddle.add(x, y, name='z')
        # z = x + y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)

        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z.name])

        print(z_value[0])
        print(z_value[0].shape) # z.shape=[2,3,4,5]


    ..  code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.random.randint(1, 5, size=[2, 3, 4, 5]).astype('float32'),
                "y": np.random.randint(1, 5, size=[5]).astype('float32')
            }

        x = fluid.data(name="x", shape=[2,3,4,5], dtype='float32')
        y = fluid.data(name="y", shape=[5], dtype='float32')
        z = paddle.add(x, y)
        # z = x / y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)

        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z.name])
        print(z_value[0])
        print(z_value[0].shape) # z.shape=[2,3,4,5]


    ..  code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        x = fluid.data(name="x", shape=[3], dtype="float32")
        y = fluid.data(name='y', shape=[3], dtype='float32')

        output = fluid.data(name="output", shape=[3], dtype="float32")
        z = paddle.add(x, y, out=output)

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)
        data1 = np.array([2, 3, 4], dtype='float32')
        data2 = np.array([1, 5, 2], dtype='float32')
        z_value = exe.run(feed={'x': data1,
                                'y': data2},
                                fetch_list=[z])
        print(z_value[0]) # [3. 8. 6.]


    ..  code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        with fluid.dygraph.guard():
            np_x = np.array([2, 3, 4]).astype('float64')
            np_y = np.array([1, 5, 2]).astype('float64')
            x = fluid.dygraph.to_variable(np_x)
            y = fluid.dygraph.to_variable(np_y)
            z = paddle.add(x, y, alpha=-0.5)
            np_z = z.numpy()
            print(np_z)  # [1.5, 0.5, 3. ]

    """
    op_type = 'elementwise_add'
    axis = -1
    act = None
    if alpha != 1:
        y = scale(y, scale=alpha)
    if in_dygraph_mode():
        return _elementwise_op_in_dygraph(
            x, y, axis=axis, act=act, op_name=op_type)

    original_op_type = 'add'
    if name and out:
        warnings.warn(
            "Both name and out parameters have been set in paddle.tensor.%s, only out will take effect to specify the result storage. "
            "You can discard either one to solve this warning." %
            original_op_type,
            category=UserWarning,
            stacklevel=2)
    return _elementwise_op(LayerHelper(op_type, **locals()))


def div(x, y, out=None, name=None):
    """
Examples:

    .. code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.array([2, 3, 4]).astype('float32'),
                "y": np.array([1, 5, 2]).astype('float32')
            }

        x = fluid.data(name="x", shape=[3], dtype='float32')
        y = fluid.data(name="y", shape=[3], dtype='float32')
        z = paddle.div(x, y)
        # z = x / y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)
        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z.name])

        print(z_value) # [2., 0.6, 2.]


    .. code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.ones((2, 3, 4, 5)).astype('float32'),
                "y": np.zeros((4, 5)).astype('float32')
            }

        x = fluid.data(name="x", shape=[2, 3, 4, 5], dtype='float32')
        y = fluid.data(name="y", shape=[4, 5], dtype='float32')
        z = paddle.div(x, y, name='z')
        # z = x / y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)

        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z.name])

        print(z_value[0])
        print(z_value[0].shape) # z.shape=[2,3,4,5]


    ..  code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        def gen_data():
            return {
                "x": np.random.randint(1, 5, size=[2, 3, 4, 5]).astype('float32'),
                "y": np.random.randint(1, 5, size=[5]).astype('float32')
            }

        x = fluid.data(name="x", shape=[2,3,4,5], dtype='float32')
        y = fluid.data(name="y", shape=[5], dtype='float32')
        output = fluid.data(name="output", shape=[2,3,4,5], dtype="float32")
        z = paddle.div(x, y, out=output)
        # z = x / y

        place = fluid.CPUPlace()
        exe = fluid.Executor(place)

        z_value = exe.run(feed=gen_data(),
                            fetch_list=[z.name])
        print(z_value[0])
        print(z_value[0].shape) # z.shape=[2,3,4,5]


    ..  code-block:: python

        import paddle
        import paddle.fluid as fluid
        import numpy as np

        with fluid.dygraph.guard(fluid.CPUPlace()):
            np_x = np.array([2, 3, 4]).astype('float64')
            np_y = np.array([1, 5, 2]).astype('float64')
            x = fluid.dygraph.to_variable(np_x)
            y = fluid.dygraph.to_variable(np_y)
            z = paddle.div(x, y)
            np_z = z.numpy()
            print(np_z)  # [2., 0.6, 2.]

    """
    op_type = 'elementwise_div'
    axis = -1
    act = None
    if in_dygraph_mode():
        return _elementwise_op_in_dygraph(
            x, y, axis=axis, act=act, op_name=op_type)

    original_op_type = 'div'
    if name and out:
        warnings.warn(
            "Both name and out parameters have been set in paddle.tensor.%s, only out will take effect to specify the result storage. "
            "You can discard either one to solve this warning." %
            original_op_type,
            category=UserWarning,
            stacklevel=2)
    return _elementwise_op(LayerHelper(op_type, **locals()))


for func in [
        add,
        div,
]:
    proto_dict = {'add': 'elementwise_add', 'div': 'elementwise_div'}
    op_proto = OpProtoHolder.instance().get_op_proto(proto_dict[func.__name__])
    if func.__name__ in ['add']:
        additional_args_lines = [
            "alpha (int|float, optional): The alpha factor of the input. Default is 1. If alpha is not 1, the equation becomes Out = X + alpha * Y.",
            "out (Variable, optinal): The Variable that stores results of the operation. Default is None. If out is None, \
            a new Variable will be created to store the results."
                                                                 ,
            "name (string, optional): Name of the output. \
            Default is None. It's used to print debug info for developers. Details: \
            :ref:`api_guide_Name` "
        ]
    else:
        additional_args_lines = [
            "out (Variable, optinal): The Variable that stores results of the operation. If out is None, \
            a new Variable will be created to store the results."
                                                                 ,
            "name (string, optional): Name of the output. \
            Default is None. It's used to print debug info for developers. Details: \
            :ref:`api_guide_Name` "
        ]

    func.__doc__ = _generate_doc_string_(
        op_proto,
        additional_args_lines=additional_args_lines,
        skip_attrs_set={"x_data_format", "y_data_format", "axis"
                        }) + """\n""" + str(func.__doc__)


def sum(input, dim=None, dtype=None, keep_dim=False, name=None):
    """
    Computes the sum of tensor elements over the given dimension.

    Args:
        input (Variable): The input variable which is a Tensor, the data type is float32,
            float64, int32, int64.
        dim (list|int, optional): The dimensions along which the sum is performed. If
            :attr:`None`, sum all elements of :attr:`input` and return a
            Tensor variable with a single element, otherwise must be in the
            range :math:`[-rank(input), rank(input))`. If :math:`dim[i] < 0`,
            the dimension to reduce is :math:`rank + dim[i]`.
        dtype(str, optional): The dtype of output tensor. The default value is None, the dtype 
            of output is the same as input tensor.
        keep_dim (bool, optional): Whether to reserve the reduced dimension in the
            output Tensor. The result tensor will have one fewer dimension
            than the :attr:`input` unless :attr:`keep_dim` is true, default
            value is False.
        name(str, optional): The default value is None.  Normally there is no need for
            user to set this property.  For more information, please refer to :ref:`api_guide_Name`

    Returns:
        Variable: Tensor, results of summation operation on the specified dim of input tensor,
        it's data type is the same as input's Tensor.

    Raises:
        ValueError, the :attr:`dtype` must be float64 or int64.
    
    Examples:
        .. code-block:: python

            import paddle
            import paddle.fluid as fluid
            # x is a Tensor variable with following elements:
            #    [[0.2, 0.3, 0.5, 0.9]
            #     [0.1, 0.2, 0.6, 0.7]]
            # Each example is followed by the corresponding output tensor.
            x = fluid.data(name='x', shape=[2, 4], dtype='float32')
            out1 = paddle.sum(x)  # [3.5]
            out2 = paddle.sum(x, dim=0)  # [0.3, 0.5, 1.1, 1.6]
            out3 = paddle.sum(x, dim=-1)  # [1.9, 1.6]
            out4 = paddle.sum(x, dim=1, keep_dim=True)  # [[1.9], [1.6]]

            # y is a Tensor variable with shape [2, 2, 2] and elements as below:
            #      [[[1, 2], [3, 4]],
            #      [[5, 6], [7, 8]]]
            # Each example is followed by the corresponding output tensor.
            y = fluid.data(name='y', shape=[2, 2, 2], dtype='float32')
            out5 = paddle.sum(y, dim=[1, 2]) # [10, 26]
            out6 = paddle.sum(y, dim=[0, 1]) # [16, 20]

    """
    if dim is not None and not isinstance(dim, list):
        dim = [dim]
    attrs = {
        'dim': dim if dim != None and dim != [] else [0],
        'keep_dim': keep_dim,
        'reduce_all': True if dim == None or dim == [] else False,
    }
    dtype_flag = False
    if dtype is not None:
        if dtype in ['float64', 'int64']:
            if (convert_dtype(input.dtype) == "float32" and dtype == "float64") or \
               (convert_dtype(input.dtype) == "int32" and dtype == "int64"):
                attrs.update({
                    'in_dtype': input.dtype,
                    'out_dtype': convert_np_dtype_to_dtype_(dtype)
                })
                dtype_flag = True
        else:
            raise ValueError(
                "The value of 'dtype' in sum op must be float64, int64, but received of {}".
                format(dtype))

    if in_dygraph_mode():
        reduce_all = True if dim == None or dim == [] else False
        dim = dim if dim != None and dim != [] else [0]
        if dtype_flag:
            return core.ops.reduce_sum(input, 'dim', dim, 'keep_dim', keep_dim,
                                       'reduce_all', reduce_all, 'in_dtype',
                                       input.dtype, 'out_dtype',
                                       convert_np_dtype_to_dtype_(dtype))
        else:
            return core.ops.reduce_sum(input, 'dim', dim, 'keep_dim', keep_dim,
                                       'reduce_all', reduce_all)
    check_variable_and_dtype(
        input, 'input', ['float32', 'float64', 'int32', 'int64'], 'reduce_sum')
    helper = LayerHelper('sum', **locals())
    if dtype_flag:
        out = helper.create_variable_for_type_inference(
            dtype=convert_np_dtype_to_dtype_(dtype))
    else:
        out = helper.create_variable_for_type_inference(dtype=input.dtype)
    helper.append_op(
        type='reduce_sum',
        inputs={'X': input},
        outputs={'Out': out},
        attrs=attrs)
    return out


@templatedoc(op_type="sum")
def elementwise_sum(inputs, name=None):
    """
    ${comment}
    
    Case 1:
    ::
        Input:
            Input. Shape = [2, 3]
            Input = [[1, 2, 3],
                     [4, 5, 6]]

        Output:
            The output. Shape = [2, 3]
            Output = [[1, 2, 3],
                      [4, 5, 6]]

    Case 2:
    ::
        Input:
            First input:
            Input1. Shape = [2, 3]
            Input1 = [[1, 2, 3],
                      [4, 5, 6]]

        The second input:
            Input2. Shape = [2, 3]
            Input2 = [[7, 8, 9],
                      [10, 11, 12]]

        Output:
            The output. Shape = [2, 3]
            Output = [[8, 10, 12],
                      [14, 16, 18]]

    Args:
        inputs (Variable|list(Variable)):  A Varaible list. The shape and data type of the list elementsshould be consistent. 
            Variable can be multi-dimensional Tensoror LoDTensor, and data types can be: float32, float64, int32, int64. 
        name(str, optional): The default value is None. Normally there is no need for
            user to set this property. For more information, please refer to :ref:`api_guide_Name`

    Returns:
        Variable: the sum of input :math:`inputs` . its shape and data types are consistent with :math:`inputs` . 

    Examples:
        .. code-block:: python

            import paddle
            import paddle.fluid as fluid

            input0 = fluid.layers.fill_constant(shape=[2, 3], dtype='int64', value=5)
            input1 = fluid.layers.fill_constant(shape=[2, 3], dtype='int64', value=3)
            sum = paddle.elementwise_sum([input0, input1])

            # You can print out 'sum' via executor.
            out = fluid.layers.Print(sum, message="the sum of input0 and input1: ")
            exe = fluid.Executor(fluid.CPUPlace())
            exe.run(fluid.default_main_program())

            # The printed result is:
            # 1570701754	the sum of input0 and input1: 	The place is:CPUPlace
            # Tensor[elementwise_sum_0.tmp_0]
            #    shape: [2,3,]
            #    dtype: l
            #    data: 8,8,8,8,8,8,

            # the sum of input0 and input1 is 2-D Tensor with shape [2,3].
            # dtype is the corresponding C++ data type, which may vary in different environments.
            # Eg: if the data type of tensor is int64, then the corresponding C++ data type is int64_t, 
            #       so the dtype value is typeid(int64_t).Name(), which is 'x' on MacOS, 'l' on Linux, 
            #       and '__int64' on Windows. They both represent 64-bit integer variables.
    """

    helper = LayerHelper('elementwise_sum', **locals())
    check_type(inputs, 'inputs', (Variable, tuple, list), 'elementwise_sum')
    if isinstance(inputs, list) or isinstance(inputs, tuple):
        if len(inputs) > 0:
            for input in inputs:
                check_variable_and_dtype(input, "inputs", \
                   ['float32', 'float64', 'int32', 'int64'], 'elementwise_sum')
    else:
        check_variable_and_dtype(inputs, "inputs", \
                ['float32', 'float64', 'int32', 'int64'], 'elementwise_sum')


    out = helper.create_variable_for_type_inference(
        dtype=helper.input_dtype('inputs'))
    helper.append_op(
        type='sum',
        inputs={'X': inputs},
        outputs={'Out': out},
        attrs={'use_mkldnn': False})

    return out


def mm(input, mat2, out=None, name=None):
    """
    Applies matrix multiplication to two tensors.

    Currently, the input tensors' rank can be any, but when the rank of any
    inputs is bigger than 3, this two inputs' rank should be equal.


    Also note that if the raw tensor :math:`x` or :math:`mat2` is rank-1 and
    nontransposed, the prepended or appended dimension :math:`1` will be
    removed after matrix multiplication.

    Args:
        x (Variable): The input variable which is a Tensor or LoDTensor.
        mat2 (Variable): The input variable which is a Tensor or LoDTensor.
        out(Variable, optional): Optional output which can be any created 
            Variable that meets the requirements to store the result of operation.
            if out is None, a new Varibale will be create to store the result.
        name(str, optional): The default value is None. Normally there is no need for
            user to set this property. For more information, please refer to :ref:`api_guide_Name`

    Returns:
        Variable: The product Tensor (or LoDTensor) variable.

    Examples:
        .. code-block:: python

            # Examples to clarify shapes of the inputs and output
            # x: [B, ..., M, K], mat2: [B, ..., K, N]
            # fluid.layers.matmul(x, mat2)  # out: [B, ..., M, N]

            # x: [B, M, K], mat2: [B, K, N]
            # fluid.layers.matmul(x, mat2)  # out: [B, M, N]

            # x: [B, M, K], mat2: [K, N]
            # fluid.layers.matmul(x, mat2)  # out: [B, M, N]

            # x: [M, K], mat2: [K, N]
            # fluid.layers.matmul(x, mat2)  # out: [M, N]

            # x: [B, M, K], mat2: [K]
            # fluid.layers.matmul(x, mat2)  # out: [B, M]

            # x: [K], mat2: [K]
            # fluid.layers.matmul(x, mat2)  # out: [1]

            import paddle
            import paddle.fluid as fluid
            x = fluid.data(name='x', shape=[2, 3], dtype='float32')
            mat2 = fluid.data(name='mat2', shape=[3, 2], dtype='float32')
            out = paddle.mm(x, mat2) # out shape is [2, 2]
    """
    if in_dygraph_mode():
        return core.ops.matmul(input, mat2)

    def __check_input(x, y):
        var_names = {'x': x, 'y': y}
        for name, val in var_names.items():
            check_variable_and_dtype(val, name,
                                     ['float16', 'float32', 'float64'], 'mm')
        x_shape = list(x.shape)
        y_shape = list(y.shape)
        if len(x_shape) == 1:
            x_shape = [1] + x_shape
        if len(y_shape) == 1:
            y_shape = y_shape + [1]

        # check the inner 2 dimensions
        if x_shape[-1] != y_shape[-2]:
            if not ((x_shape[-1] == -1) or (y_shape[-2] == -1)):
                raise ValueError(
                    "After performing an optional transpose, Input X's width should be "
                    "equal to Y's width for multiplication "
                    "prerequisites. But received X's shape: %s, Y's shape: %s\n"
                    % (x_shape, y_shape))

        if len(y_shape) > 2 and len(x_shape) > 2:
            for i, dim_x in enumerate(x_shape[:-2]):
                # don't check neg shape
                if dim_x < 0 or y_shape[i] < 0:
                    continue
                if dim_x != y_shape[i]:
                    raise ValueError(
                        "When the matrix is larger than 2 dimensions, the higher "
                        "dimensional values of the two matrices need to be equal. "
                        "But received x_shape[%d] != y_shape[%d]. X's shape: %s, "
                        "Y's shape: %s.\n" % (i, i, x_shape, y_shape))

    __check_input(input, mat2)

    helper = LayerHelper('mm', **locals())
    if out is None:
        out = helper.create_variable_for_type_inference(dtype=input.dtype)
    helper.append_op(
        type='matmul', inputs={'X': input,
                               'Y': mat2}, outputs={'Out': out})
    return out


def addmm(input, x, y, alpha=1.0, beta=1.0, name=None):
    """
    **addmm**

    This operator is used to perform matrix multiplication for input $x$ and $y$.
    $input$ is added to the final result.
    The equation is:

    ..  math::
        Out = alpha * x * y + beta * input

    $Input$, $x$ and $y$ can carry the LoD (Level of Details) information, or not. But the output only shares the LoD information with input $input$.

    Args:
        input (Variable): The input Tensor/LoDTensor to be added to the final result.
        x (Variable): The first input Tensor/LoDTensor for matrix multiplication.
        y (Variable): The second input Tensor/LoDTensor for matrix multiplication.
        alpha (float): Coefficient of $x*y$.
        beta (float): Coefficient of $input$.
        name (str, optional): Name of the output. Normally there is no need for user to set this property. For more information, please refer to :ref:`api_guide_Name`. Default is None.

    Returns:
        Variable(Tensor/LoDTensor): The output Tensor/LoDTensor of addmm op.

    Examples:
        ..  code-block:: python

            import numpy as np
            import paddle
            import paddle.fluid as fluid

            input = fluid.data(name='input', shape=[2, 2], dtype='float32')
            x = fluid.data(name='x', shape=[2, 2], dtype='float32')
            y = fluid.data(name='y', shape=[2, 2], dtype='float32')
            out = paddle.addmm( input=input, x=x, y=y, alpha=5.0, beta=0.5 )

            data_x = np.ones((2, 2)).astype(np.float32)
            data_y = np.ones((2, 2)).astype(np.float32)
            data_input = np.ones((2, 2)).astype(np.float32)

            place =  fluid.CUDAPlace(0) if fluid.core.is_compiled_with_cuda() else fluid.CPUPlace()
            exe = fluid.Executor(place)
            results = exe.run(fluid.default_main_program(), 
                              fetch_list=[out], feed={"input": data_input, 'x': data_x, "y": data_y})
            print( np.array(results[0]) )
            # [[10.5 10.5]
            # [10.5 10.5]]
    """
    inputs = {'Input': input, "X": x, "Y": y}
    attrs = {'Alpha': alpha, 'Beta': beta}

    helper = LayerHelper("addmm", **locals())
    check_variable_and_dtype(x, 'Input', ['float32', 'float64'], 'addmm')
    check_variable_and_dtype(x, 'X', ['float32', 'float64'], 'addmm')
    check_variable_and_dtype(y, 'Y', ['float32', 'float64'], 'addmm')
    out = helper.create_variable_for_type_inference(dtype=x.dtype)

    helper.append_op(
        type="addmm", inputs=inputs, attrs=attrs, outputs={"Out": out})
    return out


def logsumexp(x, dim=None, keepdim=False, out=None, name=None):
    """
This operator calculates the log of the sum of exponentials of the input Tensor.

.. math::
   logsumexp(x) = \log\sum exp(x)


Parameters:
   x (Variable): Input LoDTensor or Tensor. Must be one of the following types: float32, float64.
   dim (list|int, optional): The dimensions along which the sum is performed. If :attr:`None`, 
     sum all elements of :attr:`input` and return a Tensor variable with a single element, 
     otherwise must be in the range :math:`[-rank(input), rank(input))`. If :math:`dim[i] < 0`,
     the dimension to reduce is :math:`rank + dim[i]`.
   keep_dim (bool, optional): Whether to reserve the reduced dimension in the output Tensor. 
     The result tensor will have one fewer dimension than the :attr:`input` unless :attr:`keep_dim` 
     is true, default value is False.
   name (str, optional): The default value is None.  Normally there is no need for user to 
     set this property.  For more information, please refer to :ref:`api_guide_Name`


Examples:

.. code-block:: python

    import paddle
    import paddle.fluid as fluid
    import numpy as np
    
    with fluid.dygraph.guard():
      np_x = np.random.uniform(0.1, 1, [10]).astype(np.float32)
      x = fluid.dygraph.to_variable(np_x)
      print(paddle.logsumexp(x).numpy())


    """
    op_type = 'logsumexp'
    assert x is not None, 'x cannot be None in {}'.format(op_type)

    # reduce_sum does not support float16
    check_variable_and_dtype(x, 'x', ['float32', 'float64'], op_type)

    exp_out = layers.exp(x)
    sum_out = layers.reduce_sum(exp_out, dim, keepdim)

    if out is not None:
        check_variable_and_dtype(out, 'out', [x.dtype], op_type)
        helper = LayerHelper(op_type, **locals())
        helper.append_op(type="log", inputs={"X": sum_out}, outputs={"Out": out})
        return out

    return layers.log(sum_out, name)
