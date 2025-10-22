import json
from types import SimpleNamespace
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from app.models.intent_model import IntentExtractionResult, IntentQuery
from app.flow.state import ChatState
from app.models.intent_model import IntentQuery, IntentExtractionResult
from app.models.dish_info_model import DishData
from app.services import intent_service, restaurant_service
from app.services.intent_service import extract_query_intent
from app.services.faiss_service import extract_query_intent as faiss_extract_query_intent, search_dishes
from app.services.dish_info_service import get_dish_info
from app.services.restaurant_service import apply_filters, validate_retrieved_dishes
from app.services.faiss_service import refine_with_centroid
from app.models.exception_model import GenericException


@pytest.fixture
def sample_chat_state():
    return ChatState(
        user_id="user1",
        session_id="session_1",
        restaurant_id="rest_1",
        query="I want pizza and tell me calories."
    )

def sample_dish_data():
    return [
        DishData(
            dish_id="1",
            dish_name="Chocolate Cake",
            description="Rich chocolate cake",
            price=8.5,
            ingredients=["chocolate", "flour", "eggs"],
            serving_size="1 slice",
            availability=True,
            allergens=["nuts"],
            nutrition_facts={
                "calories": {"value": 250},
                "protein": {"value": 5},
                "fat": {"value": 10},
                "carbohydrates": {"value": 35},
            },
        ),
        DishData(
            dish_id="2",
            dish_name="Fruit Salad",
            description="Fresh mixed fruit",
            price=6.0,
            ingredients=["fruit", "honey"],
            serving_size="1 bowl",
            availability=True,
            allergens=[],
            nutrition_facts={
                "calories": {"value": 120},
                "protein": {"value": 2},
                "fat": {"value": 1},
                "carbohydrates": {"value": 25},
            },
        ),
    ]

@pytest.mark.unit
def test_intent_extraction(monkeypatch):
    """
    Test that valid LLM JSON output is correctly parsed into IntentQuery objects.

    Purpose
    -------
    Ensures that when the LLM returns valid, well-structured JSON content,
    the system correctly parses it into IntentQuery objects and returns
    an IntentExtractionResult containing the expected intents.

    Scenario
    --------
    Mock the LLM to return JSON where keys are intent types (like "menu_retrieval")
    and values are lists of sub-queries. The function should parse these into
    a structured result.

    Expected Behavior
    -----------------
    - Returns a dictionary containing an "intents" key.
    - Each intent must be an instance of `IntentQuery`.
    - The types and queries must match the JSON data.
    """
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "menu_search":["show me desserts","find me pizza"]
    })

    mock_state = ChatState(
        user_id="u1",
        session_id="s1",
        restaurant_id="rest_1",
        query="I want desserts and butter chicken info"
    )
    with patch.object(intent_service.llm, "__call__", return_value=mock_response):
        results = extract_query_intent(mock_state)
    
    intents = results["intents"].intents
    print(intents)

    assert isinstance(results["intents"],IntentExtractionResult)
    assert any(i.type == "menu_search" for i in intents)
    assert any(i.type == "dish_info" for i in intents)
    assert all(isinstance(i,IntentQuery) for i in intents)

@pytest.mark.unit
@patch('app.services.restaurant_service.llm') 
def test_validate_retrieved_dishes(mock_llm):
    query = "I want pizza dishes"
    dishes = [
        DishData(
            dish_id="d1",
            dish_name="Butter Chicken",
            ingredients=["chicken", "butter", "spices"],
        ),
        DishData(
            dish_id="d2",
            dish_name="Paneer Tikka",
            ingredients=["paneer", "spices"],
        ),
        DishData(
            dish_id="d3",
            dish_name="Chicken Biryani",
            ingredients=["chicken", "rice", "spices"],
        ),
    ]

    mock_response = MagicMock()
    mock_response.content = json.dumps([
        {"dish_id": "d1", "include": True, "reason": "chicken dish"},
        {"dish_id": "d2", "include": False, "reason": "vegetarian"},
        {"dish_id": "d3", "include": True, "reason": "contains chicken"},
    ])

    # expected_filtered = [
    #     {"dish_id":"d1","name":"Margherita Pizza","price":12.99},
    #     {"dish_id":"d2","name":"Pepperoni Pizza","price":14.99}
    # ]

    mock_llm.invoke.return_value = mock_response
    filtered_dishes = validate_retrieved_dishes(query, dishes)

    print(filtered_dishes)

    assert isinstance(filtered_dishes,list)
    assert len(filtered_dishes) == 2
    assert all(isinstance(d,DishData) for d in filtered_dishes)
    dish_ids = [d.dish_id for d in filtered_dishes]
    assert set(dish_ids) == {"d1","d3"}

def test_missing_query():
    state = ChatState(
        user_id="user1",
        session_id="session_1",
        restaurant_id="rest_1",
        query=""
    )
    with pytest.raises(Exception, match="Missing query in state during extraction."):
        extract_query_intent(state)


@patch("app.services.intent_service.llm")
def test_invalid_llm_response(mock_llm,sample_chat_state):
    mock_response = MagicMock()
    mock_response.content = "This is not JSON"
    mock_llm.invoke.return_value = mock_response

    result = extract_query_intent(sample_chat_state)

    intents = result["intents"].intents

    assert len(intents) == 1
    assert intents[0].type == "irrelevant"
    assert intents[0].query == sample_chat_state.query


@patch("app.services.intent_service.llm")
def test_only_irrelevant_query(mock_llm):
    state = ChatState(
        user_id="user1",
        session_id="session_1",
        restaurant_id="rest_1",
        query="Tell me a joke."
    )

    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "menu_search":[],
        "dish_info":[],
        "irrelevant":["Tell me a joke."]
    })

    mock_llm.invoke.return_value = mock_response

    result = extract_query_intent(state)
    intents = result["intents"].intents
    assert intents[0].type == "irrelevant"
    assert intents[0].query == "Tell me a joke."


@patch("app.services.intent_service.llm")
def test_only_menu_search(mock_llm):
    state = ChatState(
        user_id="user1",
        session_id="session_1",
        restaurant_id="rest_1",
        query="Show me all vegan options."
    )

    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "menu_search":["Show me all vegan options."],
        "dish_info":[],
        "irrelevant":[]
    })

    mock_llm.invoke.return_value = mock_response

    result = extract_query_intent(state)
    intents = result["intents"].intents
    menu_queries = [i.query for i in intents if i.type == "menu_search"]
    assert menu_queries == ["Show me all vegan options."]


def test_only_dish_info(mock_llm):
    state = ChatState(
        user_id="user1",
        session_id="session_1",
        restaurant_id="rest_1",
        query="What are the calories in the pasta?"
    )
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "menu_search":[],
        "dish_info":["How many calories are in the pasta?"],
        "irrelevant":[]
    })

    mock_llm.invoke.return_value = mock_response

    result = extract_query_intent(state)
    intents = result["intents"].intents
    dish_info_queries = [i.query for i in intents if i.type == "dish_info"]
    assert dish_info_queries == ["How many calories are in the pasta?"]


@patch("app.services.intent_service.llm")
def test_multi_part_query(mock_llm):
    state = ChatState(
        user_id="user1",
        session_id="sess_1",
        restaurant_id="rest_1",
        query="Provide pizza under $15 and also tell me the ingredients of the pasta. Also, tell me a joke."
    )

    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "menu_search":["Provide pizza under $15"],
        "dish_info":["Tell me the ingredients of the pasta."],
        "irrelevant":["Tell me a joke."]
    })

    mock_llm.invoke.return_value = mock_response

    result = extract_query_intent(state)
    intents = result["intents"].intents

    menu_queries = [i.query for i in intents if i.type == "menu_search"]
    dish_queries = [i.query for i in intents if i.type == "dish_info"]
    irrelevant_queries = [i.query for i in intents if i.type == "irrelevant"]

    assert menu_queries == ["Provide pizza under $15"]
    assert dish_queries == ["Tell me the infredients of the pasta."]
    assert irrelevant_queries == ["Tell me a joke."] 



@patch("app.services.faiss_service.llm")
def test_extract_query_intent_positive_negative_part(mock_llm):
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "positive":["pasta","salad"],
        "negative":["cheese","cream"]
    })

    mock_llm.invoke.return_value = mock_response
    intents = faiss_extract_query_intent("Pasta without cheese or cream.")

    assert "pasta" in intents.positive
    assert "cheese" in intents.negative
    assert isinstance(intents.positive,list)
    assert isinstance(intents.negative,list)


@patch("app.services.faiss_service.llm")
def test_extract_query_intent_fallback_on_error(mock_llm):
    mock_llm.invoke.side_effect = Exception("LLM Failure")

    query = "pasta without cheese or cream."
    intents = faiss_extract_query_intent(query)

    assert intents.positive == [query]
    assert intents.negative == []


@patch("app.services.faiss_service.FAISS")
@patch("app.services.faiss_service.dish_collection")
def test_search_dishes_filtered_hits(mock_collection,mock_faiss):
    mock_index = MagicMock()
    mock_index.reconstruct.return_value = np.array([0.5,0.5])
    mock_vector_store = MagicMock(index=mock_index)
    mock_vector_store.similarity_search_with_score.return_value = [
        (SimpleNamespace(metadata={"dish_id": "1", "vector_id": 1}), 0.9),
        (SimpleNamespace(metadata={"dish_id": "2", "vector_id": 2}), 0.7),
    ]

    mock_faiss.load_local.return_value = mock_vector_store

    mock_collection.find_one.side_effect = lambda q : {
        "_id":q["_id"],
        "name":f"Dish {q['_id']}"
    }

    results = search_dishes("pasta",restaurant_id="rest_1",threshold=0.8)

    assert len(results) == 1
    assert results[0].dish["_id"] == "Dish 1"
    assert results[0].score >= 0.8
    assert isinstance(results[0].embedding,np.ndarray)


@patch("app.services.faiss_service.FAISS.load_local")
def test_search_dishes_faiss_load_failure(mock_load_local):
    mock_load_local.side_effect = Exception("FAISS load error")

    with pytest.raises(GenericException):
        search_dishes("pasta")


@patch("app.services.faiss_service.embeddings")
def test_refine_with_centroid(mock_embeddings):
    mock_embeddings.embed_query.side_effect = lambda x : np.array([1,0])
    dish_hits = [
        SimpleNamespace(dish={"_id":"1"}, embedding=np.array([1,0])),
        SimpleNamespace(dish={"_id":"2"}, embedding=np.array([-1,0])),
        SimpleNamespace(dish={"_id":"3"}, embedding=np.array([0.9,0.1]))
    ]

    dish_embeddings = {
        hit.dish["_id"] : hit.embedding for hit in dish_hits
    }

    refined = refine_with_centroid(
        dish_hits,
        ["pasta"],
        dish_embeddings
    )

    assert all(hasattr(hit, "centroid_similarity") for hit in refined)
    assert all(hit.centroid_similarity > 0.3 for hit in refined)
    sims = [hit.centroid_similarity for hit in refined]
    assert sims == sorted(sims,reverse=True)



@patch("app.services.restaurant_service.llm")
def test_apply_filters_success(mock_llm,sample_dish_data):
    mock_llm.return_value = SimpleNamespace(
        content = json.dumps({
            "price": {"max": 10, "min": 0},
            "ingredients": {"include": ["chocolate"], "exclude": []},
            "allergens": {"exclude": []},
            "nutrition": {}
        })
    )

    filtered = apply_filters("show me chocolate dishes under $10",sample_dish_data)

    assert len(filtered) == 1
    assert filtered[0].dish_name == "Chocolate Cake"
    mock_llm.assert_called_once()


@patch("app.services.restaurant_service.llm")
def test_apply_filters_exclude_ingredient(mock_llm,sample_dish_data):
    mock_llm.return_value = SimpleNamespace(
        content = json.dumps({
            "price": {"max": 15, "min": 0},
            "ingredients": {"include": [], "exclude": ["chocolate"]},
            "allergens": {"exclude": []},
            "nutrition": {}
        })
    )

    filtered = apply_filters("no chocolate dishes",sample_dish_data)
    assert len(filtered) == 1
    assert filtered[0].dish_name == "Fruit Salad"

@patch("app.services.restaurant_service.llm")
def test_apply_filters_exclude_allergen(mock_llm,sample_dish_data):
    mock_llm.return_value = SimpleNamespace(
        content = json.dumps({
            "price": {"max": 20, "min": 0},
            "ingredients": {"include": [], "exclude": []},
            "allergens": {"exclude": ["nuts"]},
            "nutrition": {}
        })
    )

    filtered = apply_filters("dishes without nuts",sample_dish_data)

    assert len(filtered) == 1
    assert filtered[0].dish_name == "Fruit Salad"


@patch("app.services.restaurant_service.llm")
def test_apply_filters_nutrition_filtering(mock_llm,sample_dish_data):
    mock_llm.return_value = SimpleNamespace(
        content = json.dumps({
            "price": {"max": 50, "min": 0},
            "ingredients": {"include": [], "exclude": []},
            "allergens": {"exclude": []},
            "nutrition": {"max_calories": 200, "min_protein": 0}
        })
    )

    filtered = apply_filters("low calorie dishes",sample_dish_data)

    assert len(filtered) == 1
    assert filtered[0].dish_name == "Fruit Salad"



@patch("app.services.restaurant_service.llm")
def test_apply_filters_empty_list(mock_llm):
    results = apply_filters("whatever",[])
    assert results == []
    mock_llm.assert_not_called()


@patch("app.services.restaurant_service.llm")
def test_apply_filters_invalid_json(mock_llm,sample_dish_data):
    mock_llm.return_value = SimpleNamespace(content="Not a JSON")
    with pytest.raises(GenericException):
        apply_filters("some query",sample_dish_data)