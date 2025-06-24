import pytest

from meshmind.core.similarity import cosine_similarity, euclidean_distance


def test_cosine_similarity_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    assert cosine_similarity(v1, v2) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    v1 = [0.0, 0.0]
    v2 = [1.0, 2.0]
    assert cosine_similarity(v1, v2) == 0.0


def test_euclidean_distance_basic():
    v1 = [0.0, 0.0]
    v2 = [3.0, 4.0]
    assert euclidean_distance(v1, v2) == pytest.approx(5.0)


def test_error_on_different_lengths():
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        euclidean_distance([1.0, 2.0], [1.0, 2.0, 3.0])