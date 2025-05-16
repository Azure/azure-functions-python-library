import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.openai import (
    AssistantSkillTrigger,
    TextCompletionInput,
    OpenAIModels,
    AssistantQueryInput,
    EmbeddingsInput,
    AssistantCreateOutput,
    SemanticSearchInput,
    EmbeddingsStoreOutput,
    AssistantPostInput,
)


class TestOpenAI(unittest.TestCase):

    def test_assistant_skill_trigger_valid_creation(self):
        trigger = AssistantSkillTrigger(
            name="test",
            function_description="description",
            function_name="test_function_name",
            parameter_description_json="test_json",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(trigger.get_binding_name(), "assistantSkillTrigger")
        self.assertEqual(
            trigger.get_dict_repr(),
            {
                "name": "test",
                "functionDescription": "description",
                "functionName": "test_function_name",
                "parameterDescriptionJson": "test_json",
                "dataType": DataType.UNDEFINED,
                "type": "assistantSkillTrigger",
                "dummyField": "dummy",
                "direction": BindingDirection.IN,
            },
        )

    def test_text_completion_input_valid_creation(self):
        input = TextCompletionInput(
            name="test",
            prompt="test_prompt",
            temperature="1",
            max_tokens="1",
            is_reasoning_model=False,
            data_type=DataType.UNDEFINED,
            chat_model=OpenAIModels.DefaultChatModel,
            ai_connection_name="test_connection",
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "textCompletion")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "temperature": "1",
                "maxTokens": "1",
                "type": "textCompletion",
                "dataType": DataType.UNDEFINED,
                "dummyField": "dummy",
                "prompt": "test_prompt",
                "direction": BindingDirection.IN,
                "chatModel": OpenAIModels.DefaultChatModel,
                "isReasoningModel": False,
                "aiConnectionName": "test_connection",
            },
        )

    def test_text_completion_input_with_string_chat_model(self):
        input = TextCompletionInput(
            name="test",
            prompt="test_prompt",
            temperature="1",
            max_tokens="1",
            is_reasoning_model=True,
            data_type=DataType.UNDEFINED,
            chat_model="gpt-4o",
            ai_connection_name="test_connection",
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "textCompletion")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "temperature": "1",
                "maxTokens": "1",
                "type": "textCompletion",
                "dataType": DataType.UNDEFINED,
                "dummyField": "dummy",
                "prompt": "test_prompt",
                "direction": BindingDirection.IN,
                "chatModel": "gpt-4o",
                "isReasoningModel": True,
                "aiConnectionName": "test_connection",
            },
        )

    def test_assistant_query_input_valid_creation(self):
        input = AssistantQueryInput(
            name="test",
            timestamp_utc="timestamp_utc",
            chat_storage_connection_setting="AzureWebJobsStorage",  # noqa: E501
            collection_name="ChatState",
            data_type=DataType.UNDEFINED,
            id="test_id",
            type="assistantQueryInput",
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "assistantQuery")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "timestampUtc": "timestamp_utc",
                "chatStorageConnectionSetting": "AzureWebJobsStorage",  # noqa: E501
                "collectionName": "ChatState",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.IN,
                "type": "assistantQuery",
                "id": "test_id",
                "dummyField": "dummy",
            },
        )

    def test_embeddings_input_valid_creation(self):
        input = EmbeddingsInput(
            name="test",
            data_type=DataType.UNDEFINED,
            input="test_input",
            input_type="test_input_type",
            embeddings_model="test_model",
            max_overlap=1,
            max_chunk_length=1,
            ai_connection_name="test_connection",
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "embeddings")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "type": "embeddings",
                "dataType": DataType.UNDEFINED,
                "input": "test_input",
                "inputType": "test_input_type",
                "embeddingsModel": "test_model",
                "maxOverlap": 1,
                "maxChunkLength": 1,
                "direction": BindingDirection.IN,
                "aiConnectionName": "test_connection",
                "dummyField": "dummy",
            },
        )

    def test_embeddings_input_with_enum_embeddings_model(self):
        input = EmbeddingsInput(
            name="test",
            data_type=DataType.UNDEFINED,
            input="test_input",
            input_type="test_input_type",
            embeddings_model=OpenAIModels.DefaultEmbeddingsModel,
            max_overlap=1,
            max_chunk_length=1,
            ai_connection_name="test_connection",
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "embeddings")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "type": "embeddings",
                "dataType": DataType.UNDEFINED,
                "input": "test_input",
                "inputType": "test_input_type",
                "embeddingsModel": OpenAIModels.DefaultEmbeddingsModel,
                "maxOverlap": 1,
                "maxChunkLength": 1,
                "direction": BindingDirection.IN,
                "aiConnectionName": "test_connection",
                "dummyField": "dummy",
            },
        )

    def test_assistant_create_output_valid_creation(self):
        output = AssistantCreateOutput(
            name="test", data_type=DataType.UNDEFINED
        )
        self.assertEqual(output.get_binding_name(), "assistantCreate")
        self.assertEqual(
            output.get_dict_repr(),
            {
                "name": "test",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.OUT,
                "type": "assistantCreate",
            },
        )

    def test_assistant_post_input_valid_creation(self):
        input = AssistantPostInput(
            name="test",
            id="test_id",
            chat_model="test_model",
            chat_storage_connection_setting="AzureWebJobsStorage",  # noqa: E501
            collection_name="ChatState",
            user_message="test_message",
            temperature="1",
            max_tokens="1",
            is_reasoning_model=False,
            ai_connection_name="test_connection",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "assistantPost")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "id": "test_id",
                "chatModel": "test_model",
                "chatStorageConnectionSetting": "AzureWebJobsStorage",  # noqa: E501
                "collectionName": "ChatState",
                "userMessage": "test_message",
                "temperature": "1",
                "maxTokens": "1",
                "isReasoningModel": False,
                "aiConnectionName": "test_connection",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.IN,
                "dummyField": "dummy",
                "type": "assistantPost",
            },
        )

    def test_assistant_post_input_with_enum_chat_model(self):
        input = AssistantPostInput(
            name="test",
            id="test_id",
            chat_model=OpenAIModels.DefaultChatModel,
            chat_storage_connection_setting="AzureWebJobsStorage",  # noqa: E501
            collection_name="ChatState",
            user_message="test_message",
            temperature="1",
            max_tokens="1",
            is_reasoning_model=False,
            ai_connection_name="test_connection",
            data_type=DataType.UNDEFINED,
            dummy_field="dummy",
        )
        self.assertEqual(input.get_binding_name(), "assistantPost")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "id": "test_id",
                "chatModel": OpenAIModels.DefaultChatModel,
                "chatStorageConnectionSetting": "AzureWebJobsStorage",  # noqa: E501
                "collectionName": "ChatState",
                "userMessage": "test_message",
                "temperature": "1",
                "maxTokens": "1",
                "isReasoningModel": False,
                "aiConnectionName": "test_connection",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.IN,
                "dummyField": "dummy",
                "type": "assistantPost",
            },
        )

    def test_semantic_search_input_valid_creation(self):
        input = SemanticSearchInput(
            name="test",
            data_type=DataType.UNDEFINED,
            chat_model=OpenAIModels.DefaultChatModel,
            embeddings_model=OpenAIModels.DefaultEmbeddingsModel,  # NoQA
            collection="test_collection",
            search_connection_name="test_connection",
            system_prompt="test_prompt",
            query="test_query",
            max_knowledge_count=1,
            temperature="1",
            max_tokens="1",
            is_reasoning_model=False,
            ai_connection_name="test_connection",
            dummy_field="dummy_field",
        )
        self.assertEqual(input.get_binding_name(), "semanticSearch")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.IN,
                "dummyField": "dummy_field",
                "chatModel": OpenAIModels.DefaultChatModel,
                "embeddingsModel": OpenAIModels.DefaultEmbeddingsModel,  # NoQA
                "type": "semanticSearch",
                "collection": "test_collection",
                "searchConnectionName": "test_connection",
                "systemPrompt": "test_prompt",
                "maxKnowledgeCount": 1,
                "temperature": "1",
                "maxTokens": "1",
                "isReasoningModel": False,
                "aiConnectionName": "test_connection",
                "query": "test_query",
            },
        )

    def test_semantic_search_input_with_string_models(self):
        input = SemanticSearchInput(
            name="test",
            data_type=DataType.UNDEFINED,
            chat_model="gpt-4o",
            embeddings_model="text-embedding-3-large",
            collection="test_collection",
            search_connection_name="test_connection",
            system_prompt="test_prompt",
            query="test_query",
            max_knowledge_count=1,
            temperature="1",
            max_tokens="1",
            is_reasoning_model=True,
            ai_connection_name="test_connection",
            dummy_field="dummy_field",
        )
        self.assertEqual(input.get_binding_name(), "semanticSearch")
        self.assertEqual(
            input.get_dict_repr(),
            {
                "name": "test",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.IN,
                "dummyField": "dummy_field",
                "chatModel": "gpt-4o",
                "embeddingsModel": "text-embedding-3-large",
                "type": "semanticSearch",
                "collection": "test_collection",
                "searchConnectionName": "test_connection",
                "systemPrompt": "test_prompt",
                "maxKnowledgeCount": 1,
                "temperature": "1",
                "maxTokens": "1",
                "isReasoningModel": True,
                "aiConnectionName": "test_connection",
                "query": "test_query",
            },
        )

    def test_embeddings_store_output_valid_creation(self):
        output = EmbeddingsStoreOutput(
            name="test",
            data_type=DataType.UNDEFINED,
            input="test_input",
            input_type="test_input_type",
            store_connection_name="test_connection",
            max_overlap=1,
            max_chunk_length=1,
            collection="test_collection",
            embeddings_model=OpenAIModels.DefaultEmbeddingsModel,  # noqa: E501
            ai_connection_name="test_connection",
            dummy_field="dummy_field",
        )
        self.assertEqual(output.get_binding_name(), "embeddingsStore")
        self.assertEqual(
            output.get_dict_repr(),
            {
                "name": "test",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.OUT,
                "dummyField": "dummy_field",
                "input": "test_input",
                "inputType": "test_input_type",
                "collection": "test_collection",
                "embeddingsModel": OpenAIModels.DefaultEmbeddingsModel,  # noqa: E501
                "storeConnectionName": "test_connection",
                "maxOverlap": 1,
                "maxChunkLength": 1,
                "type": "embeddingsStore",
                "aiConnectionName": "test_connection",
            },
        )

    def test_embeddings_store_output_with_string_embeddings_model(self):
        output = EmbeddingsStoreOutput(
            name="test",
            data_type=DataType.UNDEFINED,
            input="test_input",
            input_type="test_input_type",
            store_connection_name="test_connection",
            max_overlap=1,
            max_chunk_length=1,
            collection="test_collection",
            embeddings_model="text-embedding-3-small",
            ai_connection_name="test_connection",
            dummy_field="dummy_field",
        )
        self.assertEqual(output.get_binding_name(), "embeddingsStore")
        self.assertEqual(
            output.get_dict_repr(),
            {
                "name": "test",
                "dataType": DataType.UNDEFINED,
                "direction": BindingDirection.OUT,
                "dummyField": "dummy_field",
                "input": "test_input",
                "inputType": "test_input_type",
                "collection": "test_collection",
                "embeddingsModel": "text-embedding-3-small",
                "storeConnectionName": "test_connection",
                "maxOverlap": 1,
                "maxChunkLength": 1,
                "type": "embeddingsStore",
                "aiConnectionName": "test_connection",
            },
        )
