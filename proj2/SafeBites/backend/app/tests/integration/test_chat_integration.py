import pytest, json
from unittest.mock import patch, MagicMock
from app.services import intent_service, faiss_service, restaurant_service, retrieval_service, dish_info_service
from app.flow.state import ChatState
from app.models.dish_info_model import DishData, DishInfoResponse, DishInfoResult
from app.models.restaurant_model import MenuResultResponse
from app.models.exception_model import GenericException, NotFoundException

@pytest.fixture
def mock_chat_state():
    return ChatState(user_id="u123", session_id="s123", restaurant_id="r123", query="List pizza dishes.Also, does any dish contain nuts?",
                          context=[], current_context="", query_parts={"menu_search": ["List pizza dishes"], "dish_info": ["does any dish contain nuts?"]})


@pytest.fixture
def sample_dishes():
    return [
        MagicMock(
            dish = {
                "_id": "1",
                "name": "Margherita Pizza",
                "description": "Classic cheese pizza",
                "price": 10.5,
                "ingredients": ["cheese", "flour", "tomato"],
                "serving_size": "1 regular",
                "availaibility": True,
                "inferred_allergens": [{"allergen": "milk"}],
                "nutrition_facts": {"calories": {"value": 250}},
            }
        )
    ]


@patch("app.services.retrieval_service.semantic_retrieve_with_negation")
@patch("app.services.retrieval_service.apply_filters")
@patch("app.services.retrieval_service.validate_retrieved_dishes")
def test_get_menu_items_success(mock_validate, mock_filter, mock_semantic, mock_chat_state, sample_dishes):
    mock_semantic.return_value = sample_dishes

    filtered_dishes = [
        DishData(
            dish_id="1",
            dish_name="Margherita Pizza",
            description="Classic cheese pizza",
            price=10.5,
            ingredients=["cheese", "flour", "tomato"],
            serving_size="1 regular",
            availability=True,
            allergens=["milk"],
            nutrition_facts={"calories": {"value": 250}},
        )
    ]
    mock_filter.return_value = filtered_dishes
    mock_validate.return_value = filtered_dishes

    result = retrieval_service.get_menu_items(mock_chat_state)

    print(result)
    assert isinstance(result, MenuResultResponse)
    assert "List pizza dishes" in result.menu_results
    assert len(result.menu_results["List pizza dishes"]) == 1
    assert result.menu_results["List pizza dishes"][0].dish_name == "Margherita Pizza"

    mock_semantic.assert_called_once()
    mock_filter.assert_called_once()
    mock_validate.assert_called_once()


@patch("app.services.retrieval_service.semantic_retrieve_with_negation", side_effect=Exception("FAISS failure"))
def test_get_menu_items_error_handling(mock_sementic, mock_chat_state):
    result = retrieval_service.get_menu_items(mock_chat_state)
    assert isinstance(result, MenuResultResponse)
    assert "List pizza dishes" in result.menu_results
    assert result.menu_results["List pizza dishes"] == []


@patch("app.services.dish_info_service.llm")
@patch("app.services.dish_info_service.validate_retrieved_dishes")
@patch("app.services.dish_info_service.apply_filters")
@patch("app.services.dish_info_service.handle_food_item_query")
@patch("app.services.dish_info_service.derive_dish_info_intent")
def test_dish_info_success(mock_intent, mock_handle_food, mock_filter, mock_validate, mock_llm, mock_chat_state):
    mock_intent.return_value = MagicMock(type="dish_info")

    dish = DishData(
        dish_id="1",
        dish_name="Margherita Pizza",
        description="Classic cheese pizza",
        price=10.5,
        ingredients=["cheese", "flour", "tomato"],
        serving_size="1 regular",
        availability=True,
        allergens=["milk"],
        nutrition_facts={"calories": {"value": 250}},
    )

    mock_handle_food.return_value = [dish]
    mock_filter.return_value = [dish]
    mock_validate.return_value = [dish]

    llm_response = MagicMock()
    llm_response.content = json.dumps({
        "dish_name":"Margherita Pizza",
        "requested_info":"Does not contains nuts",
    })

    mock_llm.invoke.return_value = llm_response

    result = dish_info_service.get_dish_info(mock_chat_state)
    print(result)
    assert "info_results" in result
    info_results = result["info_results"].info_results
    assert "does any dish contain nuts?" in info_results

    response = info_results["does any dish contain nuts?"]
    assert isinstance(response,DishInfoResponse)
    assert response.dish_name == "Margherita Pizza"


    mock_intent.assert_called_once_with("does any dish contain nuts?")
    mock_handle_food.assert_called_once_with("does any dish contain nuts?",restaurant_id = "r123")
    mock_filter.assert_called_once()
    mock_validate.assert_called_once()
    mock_llm.invoke.assert_called_once()


@patch("app.services.dish_info_service.handle_general_knowledge")
@patch("app.services.dish_info_service.derive_dish_info_intent")
def test_get_dish_info_general_knowledge(mock_intent,mock_general,mock_chat_state):
    mock_chat_state.query_parts = {"dish_info":["What is sushi??"]}
    mock_intent.return_value = MagicMock(type="general_knowledge")
    mock_general.return_value = MagicMock(answer="Sushi is a Japanese dish made with vinegared rice.")

    results = dish_info_service.get_dish_info(mock_chat_state)

    info_results = results["info_results"].info_results
    resp = info_results["What is sushi??"]

    assert resp.requested_info == "Sushi is a Japanese dish made with vinegared rice."
    mock_general.assert_called_once()


@patch("app.services.dish_info_service.derive_dish_info_intent")
def test_get_dish_info_generic_exception(mock_intent, mock_chat_state):
    mock_chat_state.query_parts = {"dish_info":["What is sushi??"]}
    mock_intent.side_effect = GenericException("Intent derivation failed")

    results = dish_info_service.get_dish_info(mock_chat_state)

    info_results = results["info_results"].info_results
    resp = info_results["What is sushi??"]
    assert "Intent derivation failed" in resp.requested_info


@patch("app.services.dish_info_service.derive_dish_info_intent")
@patch("app.services.dish_info_service.handle_food_item_query")
def test_get_dish_info_not_found(mock_handle_food, mock_intent, mock_chat_state):
    mock_chat_state.query_parts = {"dish_info":["What is sushi??"]}
    mock_intent.return_value = MagicMock(type="dish_info")
    mock_handle_food.side_effect = NotFoundException("No dishes found")

    results = dish_info_service.get_dish_info(mock_chat_state)

    info_results = results["info_results"].info_results
    resp = info_results["What is sushi??"]
    assert resp.requested_info == "No dishes found"