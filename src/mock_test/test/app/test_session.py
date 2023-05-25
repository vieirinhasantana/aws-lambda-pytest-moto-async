from src.mock_test.app.session import Session


def test_singleton_session_aiobotocore():
    singleton_session = Session()

    session_1 = singleton_session.session
    session_2 = singleton_session.session
    assert session_1 == session_2
