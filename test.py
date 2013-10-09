from nose.tools import assert_equal

from district_borders import (
    polygons_to_graph,
    graph_edges,
    segment_lattice_points,
    merge_corners_onto_borders,
    continue_straight_lines,
)


def test_polygons_to_graph():
    #   012345
    # 0 A--B-C
    # 1 |  | |
    # 2 D--E-F
    # 3 |    |
    # 4 |    |
    # 5 G----H
    a = (0, 0)
    b = (3, 0)
    c = (5, 0)
    d = (0, 2)
    e = (3, 2)
    f = (5, 2)
    g = (0, 5)
    h = (5, 5)
    polygons = [
        [a, b, e, d],
        [b, c, f, e],
        [d, f, h, g],
    ]
    graph = polygons_to_graph(polygons)
    assert_equal(
        graph,
        {
            a: {b, d},
            b: {a, c, e},
            c: {b, f},
            d: {a, e, f, g},
            e: {b, d, f},
            f: {c, e, d, h},
            g: {d, h},
            h: {g, f},
        }
    )


def test_graph_edges():
    a, b, c, d, e = range(5)

    cases = [
        (
            {a: {b}, b: {a}},
            [(a, b)]
        ),
        (
            {
                a: {b}, b: {a},
                c: {d}, d: {c},
            },
            [(a, b), (c, d)],
        ),
        (
            {
                a: {b, c},
                b: {a, c},
                c: {a, b},
            },
            [(a, b), (a, c), (b, c)],
        ),
    ]
    for graph, target_edges in cases:
        def test(target_edges):
            assert_equal(sorted(graph_edges(graph)), target_edges)
        yield test, target_edges


def test_segment_lattice_points():
    assert_equal(
        segment_lattice_points((0, 0), (0, 4)),
        [(0, 1), (0, 2), (0, 3)],
    )
    assert_equal(
        segment_lattice_points((2, 2), (5, 2)),
        [(3, 2), (4, 2)],
    )
    assert_equal(
        segment_lattice_points((-3, -3), (3, 3)),
        [(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)]
    )
    assert_equal(
        segment_lattice_points((0, 0), (6, 12)),
        [(1, 2), (2, 4), (3, 6), (4, 8), (5, 10)],
    )
    assert_equal(
        segment_lattice_points((0, 0), (4, 6)),
        [(2, 3)],
    )
    assert_equal(
        segment_lattice_points((0, 0), (5, 13)),
        [],
    )


def test_merge_corners_onto_borders():
    #   01234567
    # 0 A-B-C
    # 1   |
    # 2   D
    a = (0, 0)
    b = (2, 0)
    c = (4, 0)
    d = (2, 2)
    graph = {
        a: {c}, c: {a},
        b: {d}, d: {b},
    }
    merge_corners_onto_borders(graph)
    assert_equal(
        graph,
        {
            a: {b},
            b: {a, c, d},
            c: {b},
            d: {b},
        }
    )

    #   01234567
    # 0 A-B-C-D
    # 1   | |
    # 2   E F
    a = (0, 0)
    b = (2, 0)
    c = (4, 0)
    d = (6, 0)
    e = (2, 2)
    f = (4, 2)
    graph = {
        a: {d}, d: {a},
        b: {e}, e: {b},
        c: {f}, f: {c},
    }
    merge_corners_onto_borders(graph)
    assert_equal(
        graph,
        {
            a: {b},
            b: {a, c, e},
            c: {b, d, f},
            d: {c},
            e: {b},
            f: {c},
        }
    )


def test_continue_straight_lines():
    # Line ACD is joined to create line AD.

    #   01234
    # 0   A
    # 1   |
    # 2 B-C
    # 3   |\
    # 4   D E
    a = (2, 0)
    b = (0, 2)
    c = (2, 2)
    d = (2, 4)
    e = (4, 4)
    graph = {
        a: {c},
        b: {c},
        c: {a, b, d, e},
        d: {c},
        e: {c},
    }
    continue_straight_lines(graph)
    assert_equal(
        graph,
        {
            a: {d}, d: {a},
            b: {c},
            c: {b, e},
            e: {c},
        }
    )
