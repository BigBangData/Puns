import os

os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret')

import pytest

from app import Puns, User, app, db


@pytest.fixture
def logged_in_client():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(username='progress-user', password='unused')
        db.session.add(user)
        db.session.add_all([
            Puns(id=1, question='First pun', answer='First answer'),
            Puns(id=2, question='Second pun', answer='Second answer'),
        ])
        db.session.commit()
        user_id = user.id

    with app.test_client() as client:
        with client.session_transaction() as browser_session:
            browser_session['_user_id'] = str(user_id)
            browser_session['_fresh'] = True
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def rate_current_pun(client):
    return client.post('/play', data={'feedback': 'no'}, follow_redirects=True)


def test_intro_progress_and_completion_restart_cycle(logged_in_client):
    client = logged_in_client

    intro = client.get('/play')
    assert b'Click to play a pun game' in intro.data
    assert b'aria-valuenow="0"' in intro.data
    assert intro.data.count(b'pun-progress-square') == 2
    assert b'First pun' not in intro.data

    first_pun = client.post('/start', follow_redirects=True)
    assert b'First pun' in first_pun.data
    assert b'aria-valuenow="0"' in first_pun.data
    assert b'data-pun-id="1"' in first_pun.data

    answer = client.post('/view_answer')
    assert b'First answer' in answer.data
    assert b'aria-valuenow="0"' in answer.data

    second_pun = rate_current_pun(client)
    assert b'Second pun' in second_pun.data
    assert b'aria-valuenow="50"' in second_pun.data
    assert second_pun.data.count(b'pun-progress-square completed') == 1
    assert b'data-pun-id="1"' in second_pun.data
    assert b'data-pun-id="2"' in second_pun.data

    completion = rate_current_pun(client)
    assert b"pun-ultimate" in completion.data
    assert b'Click to play a pun game' in completion.data
    assert b'aria-valuenow="0"' in completion.data

    restarted = client.post('/start', follow_redirects=True)
    assert b'First pun' in restarted.data
    assert b'aria-valuenow="0"' in restarted.data


def test_progress_grid_renders_300_pun_squares(logged_in_client):
    with app.app_context():
        db.session.add_all([
            Puns(id=pun_id, question='Another pun', answer='Another answer')
            for pun_id in range(3, 301)
        ])
        db.session.commit()

    response = logged_in_client.get('/play')

    assert response.data.count(b'pun-progress-square') == 300
    assert b'aria-label="Jump to pun 300"' in response.data
    assert b'>300</button>' in response.data
    assert b'Jump to pun number' in response.data


def test_jump_to_pun_by_number(logged_in_client):
    response = logged_in_client.post('/jump', data={'pun_id': '2'}, follow_redirects=True)

    assert b'Second pun' in response.data
    assert b'data-pun-id="2"' in response.data
    assert b'aria-current="true"' in response.data

    answer = logged_in_client.post('/view_answer')
    assert b'Second answer' in answer.data


def test_jump_rejects_unknown_pun_number(logged_in_client):
    response = logged_in_client.post('/jump', data={'pun_id': '999'}, follow_redirects=True)

    assert b'Please choose an available pun number.' in response.data
    assert b'Click to play a pun game' in response.data
