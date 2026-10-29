from datetime import datetime, timedelta

from db.seed import DEMO_EMAIL
from tests.conftest import login


def test_saved_favourite_is_listed_with_full_product_details(client, demo_headers):
    saved = client.post("/api/favourites/3", headers=demo_headers)
    assert saved.status_code == 200, saved.text

    listed = client.get("/api/favourites", headers=demo_headers)

    assert listed.status_code == 200, listed.text
    [favourite] = listed.json()
    product = next(
        item
        for item in client.get("/api/catalog/items").json()["items"]
        if item["id"] == 3
    )
    assert {k: favourite[k] for k in product} == product


def test_anonymous_callers_are_refused(client, anon_headers):
    assert client.get("/api/favourites", headers=anon_headers).status_code == 401
    assert client.post("/api/favourites/3", headers=anon_headers).status_code == 401
    assert client.get("/api/favourites").status_code == 401


def test_saving_an_unknown_product_is_404(client, demo_headers):
    response = client.post("/api/favourites/99999", headers=demo_headers)

    assert response.status_code == 404
    assert client.get("/api/favourites", headers=demo_headers).json() == []


def test_saving_the_same_product_twice_leaves_one_favourite(client, demo_headers):
    first = client.post("/api/favourites/3", headers=demo_headers)
    second = client.post("/api/favourites/3", headers=demo_headers)

    assert first.status_code == second.status_code == 200
    assert len(client.get("/api/favourites", headers=demo_headers).json()) == 1


def test_favourites_list_newest_saved_first_with_utc_timestamps(client, demo_headers):
    for product_id in (3, 1, 2):
        client.post(f"/api/favourites/{product_id}", headers=demo_headers)

    listed = client.get("/api/favourites", headers=demo_headers).json()

    assert [f["id"] for f in listed] == [2, 1, 3]
    stamps = [datetime.fromisoformat(f["created_at"].replace("Z", "+00:00")) for f in listed]
    assert all(s.utcoffset() == timedelta(0) for s in stamps)
    assert stamps == sorted(stamps, reverse=True)


def test_one_account_never_sees_anothers_favourites(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)
    client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "password": "correct-horse-battery"},
    )
    other = login(client, "other@example.com", "correct-horse-battery")

    assert client.get("/api/favourites", headers=other).json() == []

    client.post("/api/favourites/1", headers=other)
    assert [f["id"] for f in client.get("/api/favourites", headers=demo_headers).json()] == [3]


def test_an_email_as_basket_id_cannot_reach_favourites(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)
    spoof = {"X-Basket-Id": DEMO_EMAIL}

    assert client.get("/api/favourites", headers=spoof).status_code == 401
    assert client.post("/api/favourites/1", headers=spoof).status_code == 401
    assert [f["id"] for f in client.get("/api/favourites", headers=demo_headers).json()] == [3]


def test_favourites_and_basket_do_not_affect_each_other(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)
    assert client.get("/api/basket", headers=demo_headers).json()["items"] == []

    client.post("/api/basket/items", json={"catalog_item_id": 1}, headers=demo_headers)

    assert [f["id"] for f in client.get("/api/favourites", headers=demo_headers).json()] == [3]


def test_removed_favourite_no_longer_appears_in_the_list(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)
    client.post("/api/favourites/1", headers=demo_headers)

    removed = client.delete("/api/favourites/3", headers=demo_headers)

    assert removed.status_code == 200, removed.text
    assert [f["id"] for f in client.get("/api/favourites", headers=demo_headers).json()] == [1]


def test_removing_a_product_that_is_not_a_favourite_is_a_no_op(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)

    never_saved = client.delete("/api/favourites/1", headers=demo_headers)
    unknown = client.delete("/api/favourites/99999", headers=demo_headers)

    assert never_saved.status_code == unknown.status_code == 200
    assert [f["id"] for f in client.get("/api/favourites", headers=demo_headers).json()] == [3]


def test_favourite_ids_match_the_full_list(client, demo_headers):
    for product_id in (3, 1, 2):
        client.post(f"/api/favourites/{product_id}", headers=demo_headers)

    ids = client.get("/api/favourites/ids", headers=demo_headers)

    assert ids.status_code == 200, ids.text
    listed = client.get("/api/favourites", headers=demo_headers).json()
    assert ids.json() == [f["id"] for f in listed] == [2, 1, 3]


def test_anonymous_callers_cannot_remove_or_list_ids(client, anon_headers):
    assert client.delete("/api/favourites/3", headers=anon_headers).status_code == 401
    assert client.get("/api/favourites/ids", headers=anon_headers).status_code == 401
    assert client.get("/api/favourites/ids").status_code == 401


def test_favourites_are_still_there_after_signing_in_again(client, demo_headers):
    client.post("/api/favourites/3", headers=demo_headers)

    fresh = login(client)

    assert [f["id"] for f in client.get("/api/favourites", headers=fresh).json()] == [3]
