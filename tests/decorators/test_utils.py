#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions import HttpMethod
from azure.functions.decorators import utils
from azure.functions.decorators.constants import HTTP_TRIGGER
from azure.functions.decorators.core import DataType, Trigger
from azure.functions.decorators.generic import GenericTrigger
from azure.functions.decorators.http import HttpTrigger
from azure.functions.decorators.utils import to_camel_case, BuildDictMeta, \
    is_snake_case, is_word


class TestUtils(unittest.TestCase):
    def test_parse_singular_none_to_enum(self):
        self.assertEqual(utils.parse_singular_param_to_enum(None, DataType),
                         None)

    def test_parse_singular_str_to_enum_str(self):
        self.assertEqual(
            utils.parse_singular_param_to_enum('STRING', DataType),
            DataType.STRING)

    def test_parse_singular_lowercase_str_to_enum_str(self):
        self.assertEqual(
            utils.parse_singular_param_to_enum('string', DataType),
            DataType.STRING)

    def test_parse_singular_enum_to_enum(self):
        self.assertEqual(
            utils.parse_singular_param_to_enum(DataType.STRING, DataType),
            DataType.STRING)

    def test_parse_singular_invalid_param_to_enum(self):
        with self.assertRaises(KeyError) as err:
            self.assertEqual(
                utils.parse_singular_param_to_enum('dummy', DataType),
                DataType.STRING)

        self.assertEqual(err.exception.args[0],
                         "Can not parse str 'dummy' to DataType. "
                         f"Allowed values are {[e.name for e in DataType]}")

    def test_parse_none_to_enums(self):
        self.assertEqual(
            utils.parse_iterable_param_to_enums(None, HttpMethod), None)

    def test_parse_iterable_str_to_enums(self):
        self.assertEqual(
            utils.parse_iterable_param_to_enums(['GET', 'POST'], HttpMethod),
            [HttpMethod.GET, HttpMethod.POST])

    def test_parse_iterable_lowercase_str_to_enums(self):
        self.assertEqual(
            utils.parse_iterable_param_to_enums(['get', 'post'], HttpMethod),
            [HttpMethod.GET, HttpMethod.POST])

    def test_parse_iterable_enums_to_enums(self):
        self.assertEqual(
            utils.parse_iterable_param_to_enums(
                [HttpMethod.GET, HttpMethod.POST], HttpMethod),
            [HttpMethod.GET, HttpMethod.POST])

    def test_parse_invalid_iterable_param_to_enums(self):
        with self.assertRaises(KeyError) as err:
            self.assertEqual(
                utils.parse_iterable_param_to_enums(['dummy'], HttpMethod),
                DataType.STRING)

        self.assertEqual(err.exception.args[0],
                         "Can not parse '['dummy']' to Optional["
                         "Iterable["
                         f"{HttpMethod.__name__}]]. "
                         f"Please ensure param all list elements exist in "
                         f"{[e.name for e in HttpMethod]}")

    def test_snake_case_to_camel_case_multi(self):
        self.assertEqual(to_camel_case("data_type"), "dataType")

    def test_snake_case_to_camel_case_trailing_underscore(self):
        self.assertEqual(to_camel_case("data_type_"), "dataType")

    def test_snake_case_to_camel_case_leading_underscore(self):
        self.assertEqual(to_camel_case("_dataType"), "Datatype")

    def test_snake_case_to_camel_case_single(self):
        self.assertEqual(to_camel_case("dataType"), "dataType")

    def test_snake_case_to_camel_case_empty_str(self):
        with self.assertRaises(ValueError) as err:
            to_camel_case("")
        self.assertEqual(err.exception.args[0],
                         'Please ensure arg name  is not '
                         'empty!')

    def test_snake_case_to_camel_case_none(self):
        with self.assertRaises(ValueError) as err:
            to_camel_case(None)
        self.assertEqual(err.exception.args[0],
                         'Please ensure arg name None is not '
                         'empty!')

    def test_snake_case_to_camel_case_not_one_word_nor_snake_case(self):
        with self.assertRaises(ValueError) as err:
            to_camel_case("data-type")
        self.assertEqual(err.exception.args[0],
                         'Please ensure data-type is a word or snake case '
                         'string with underscore as separator.')

    def test_is_snake_case_letters_only(self):
        self.assertTrue(is_snake_case("dataType_foo"))

    def test_is_snake_case_lowercase_with_digit(self):
        self.assertTrue(is_snake_case("data_type_233"))

    def test_is_snake_case_uppercase_with_digit(self):
        self.assertTrue(is_snake_case("Data_Type_233"))

    def test_is_snake_case_leading_digit(self):
        self.assertFalse(is_snake_case("233_Data_Type_233"))

    def test_is_snake_case_no_separator(self):
        self.assertFalse(is_snake_case("DataType233"))

    def test_is_snake_case_invalid_separator(self):
        self.assertFalse(is_snake_case("Data-Type-233"))

    def test_is_word_letters_only(self):
        self.assertTrue(is_word("dataType"))

    def test_is_word_letters_with_digits(self):
        self.assertTrue(is_word("dataType233"))

    def test_is_word_leading_digits(self):
        self.assertFalse(is_word("233dataType"))

    def test_is_word_invalid_symbol(self):
        self.assertFalse(is_word("233!dataType"))

    def test_clean_nones_none(self):
        self.assertEqual(BuildDictMeta.clean_nones(None), None)

    def test_clean_nones_nested(self):
        self.assertEqual(BuildDictMeta.clean_nones(
            {
                "hello": None,
                "hello2": ["dummy1", None, "dummy2", ["dummy3", None],
                           {"hello3": None}],
                "hello4": {
                    "dummy5": "pass1",
                    "dummy6": None
                }
            }),
            {
                "hello2": ["dummy1", "dummy2", ["dummy3"], {}],
                "hello4": {"dummy5": "pass1"}
            }  # NoQA
        )

    def test_add_to_dict_no_args(self):
        with self.assertRaises(ValueError) as err:
            @BuildDictMeta.add_to_dict
            def dummy():
                pass

            dummy()

        self.assertEqual(err.exception.args[0],
                         'dummy has no args. Please ensure func is an object '
                         'method.')

    def test_add_to_dict_valid(self):
        class TestDict:
            @BuildDictMeta.add_to_dict
            def __init__(self, arg1, arg2, **kwargs):
                self.arg1 = arg1
                self.arg2 = arg2

        test_obj = TestDict('val1', 'val2', dummy1="dummy1", dummy2="dummy2")

        self.assertCountEqual(getattr(test_obj, 'init_params'),
                              {'self', 'arg1', 'arg2', 'kwargs', 'dummy1',
                               'dummy2'})
        self.assertEqual(getattr(test_obj, "arg1", None), "val1")
        self.assertEqual(getattr(test_obj, "arg2", None), "val2")
        self.assertEqual(getattr(test_obj, "dummy1", None), "dummy1")
        self.assertEqual(getattr(test_obj, "dummy2", None), "dummy2")

    def test_build_dict_meta(self):
        class TestBuildDict(metaclass=BuildDictMeta):
            def __init__(self, arg1, arg2):
                pass

            def get_dict_repr(self):
                return {
                    "hello": None,
                    "world": ["dummy", None]
                }

        test_obj = TestBuildDict('val1', 'val2')

        self.assertCountEqual(getattr(test_obj, 'init_params'),
                              {'self', 'arg1', 'arg2'})
        self.assertEqual(test_obj.get_dict_repr(), {"world": ["dummy"]})

    def test_is_supported_trigger_binding_name(self):
        self.assertTrue(
            Trigger.is_supported_trigger_type(
                GenericTrigger(name='req', type=HTTP_TRIGGER), HttpTrigger))

    def test_is_supported_trigger_instance(self):
        self.assertTrue(
            Trigger.is_supported_trigger_type(HttpTrigger(name='req'),
                                              HttpTrigger))

    def test_is_not_supported_trigger_type(self):
        self.assertFalse(
            Trigger.is_supported_trigger_type(
                GenericTrigger(name='req', type="dummy"),
                HttpTrigger))
