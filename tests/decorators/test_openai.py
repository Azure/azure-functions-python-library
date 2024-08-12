import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.openai import AssistantSkillTrigger, \
    TextCompletionInput, OpenAIModels, AssistantQueryInput, EmbeddingsInput, \
    AssistantCreateOutput, SemanticSearchInput, EmbeddingsStoreOutput, \
    AssistantPostInput


class TestOpenAI(unittest.TestCase):

    def test_assistant_skill_trigger_valid_creation(self):
        trigger = AssistantSkillTrigger(name="test",
                                        function_description="description",
                                        function_name="test_function_name",
                                        parameter_description_json="test_json",
                                        model=OpenAIModels.DefaultChatModel,
                                        data_type=DataType.UNDEFINED,
                                        dummy_field="dummy")
        self.assertEqual(trigger.get_binding_name(),
                         "assistantSkillTrigger")
        self.assertEqual(
            trigger.get_dict_repr(), {"name": "test",
                                      "functionDescription": "description",
                                      "functionName": "test_function_name",
                                      "parameterDescriptionJson": "test_json",
                                      "model": OpenAIModels.DefaultChatModel,
                                      "dataType": DataType.UNDEFINED,
                                      'type': 'assistantSkillTrigger',
                                      'dummyField': 'dummy',
                                      "direction": BindingDirection.IN,
                                      })

    def test_text_completion_input_valid_creation(self):
        input = TextCompletionInput(name="test",
                                    prompt="test_prompt",
                                    temperature="1",
                                    max_tokens="1",
                                    data_type=DataType.UNDEFINED,
                                    model=OpenAIModels.DefaultChatModel,
                                    dummy_field="dummy")
        self.assertEqual(input.get_binding_name(),
                         "textCompletion")
        self.assertEqual(input.get_dict_repr(),
                         {"name": "test",
                          "temperature": "1",
                          "maxTokens": "1",
                          'type': 'textCompletion',
                          "dataType": DataType.UNDEFINED,
                          "dummyField": "dummy",
                          "prompt": "test_prompt",
                          "direction": BindingDirection.IN,
                          "model": OpenAIModels.DefaultChatModel
                          })

    def test_assistant_query_input_valid_creation(self):
        input = AssistantQueryInput(name="test",
                                    timestamp_utc="timestamp_utc",
                                    data_type=DataType.UNDEFINED,
                                    id="test_id",
                                    type="assistantQueryInput",
                                    dummy_field="dummy")
        self.assertEqual(input.get_binding_name(),
                         "assistantQuery")
        self.assertEqual(input.get_dict_repr(),
                         {"name": "test",
                          "timestampUtc": "timestamp_utc",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "type": "assistantQuery",
                          "id": "test_id",
                          "dummyField": "dummy"
                          })

    def test_embeddings_input_valid_creation(self):
        input = EmbeddingsInput(name="test",
                                data_type=DataType.UNDEFINED,
                                input="test_input",
                                input_type="test_input_type",
                                model="test_model",
                                max_overlap=1,
                                max_chunk_length=1,
                                dummy_field="dummy")
        self.assertEqual(input.get_binding_name(),
                         "embeddings")
        self.assertEqual(input.get_dict_repr(),
                         {"name": "test",
                          "type": "embeddings",
                          "dataType": DataType.UNDEFINED,
                          "input": "test_input",
                          "inputType": "test_input_type",
                          "model": "test_model",
                          "maxOverlap": 1,
                          "maxChunkLength": 1,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy"})

    def test_assistant_create_output_valid_creation(self):
        output = AssistantCreateOutput(name="test",
                                       data_type=DataType.UNDEFINED)
        self.assertEqual(output.get_binding_name(),
                         "assistantCreate")
        self.assertEqual(output.get_dict_repr(),
                         {"name": "test",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.OUT,
                          "type": "assistantCreate"})

    def test_assistant_post_input_valid_creation(self):
        input = AssistantPostInput(name="test",
                                   id="test_id",
                                   model="test_model",
                                   user_message="test_message",
                                   data_type=DataType.UNDEFINED,
                                   dummy_field="dummy")
        self.assertEqual(input.get_binding_name(),
                         "assistantPost")
        self.assertEqual(input.get_dict_repr(),
                         {"name": "test",
                          "id": "test_id",
                          "model": "test_model",
                          "userMessage": "test_message",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy",
                          "type": "assistantPost"})

    def test_semantic_search_input_valid_creation(self):
        input = SemanticSearchInput(name="test",
                                    data_type=DataType.UNDEFINED,
                                    chat_model=OpenAIModels.DefaultChatModel,
                                    embeddings_model=OpenAIModels.DefaultEmbeddingsModel,  # NoQA
                                    collection="test_collection",
                                    connection_name="test_connection",
                                    system_prompt="test_prompt",
                                    query="test_query",
                                    max_knowledge_count=1,
                                    dummy_field="dummy_field")
        self.assertEqual(input.get_binding_name(),
                         "semanticSearch")
        self.assertEqual(input.get_dict_repr(),
                         {"name": "test",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy_field",
                          "chatModel": OpenAIModels.DefaultChatModel,
                          "embeddingsModel": OpenAIModels.DefaultEmbeddingsModel,  # NoQA
                          "type": "semanticSearch",
                          "collection": "test_collection",
                          "connectionName": "test_connection",
                          "systemPrompt": "test_prompt",
                          "maxKnowledgeCount": 1,
                          "query": "test_query"})

    def test_embeddings_store_output_valid_creation(self):
        output = EmbeddingsStoreOutput(name="test",
                                       data_type=DataType.UNDEFINED,
                                       input="test_input",
                                       input_type="test_input_type",
                                       connection_name="test_connection",
                                       max_overlap=1,
                                       max_chunk_length=1,
                                       collection="test_collection",
                                       model=OpenAIModels.DefaultChatModel,
                                       dummy_field="dummy_field")
        self.assertEqual(output.get_binding_name(),
                         "embeddingsStore")
        self.assertEqual(output.get_dict_repr(),
                         {"name": "test",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.OUT,
                          "dummyField": "dummy_field",
                          "input": "test_input",
                          "inputType": "test_input_type",
                          "collection": "test_collection",
                          "model": OpenAIModels.DefaultChatModel,
                          "connectionName": "test_connection",
                          "maxOverlap": 1,
                          "maxChunkLength": 1,
                          "type": "embeddingsStore"})
