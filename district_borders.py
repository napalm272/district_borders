def polygons_to_graph(polygons):
    """
    Construct a graph out of a list of polygons. Each polygon is specified as a
    list of points in clockwise order.
    """
    graph = {}

    # Initialize graph nodes.
    for poly in polygons:
        for p in poly:
            graph[p] = set()

    # Add edges.
    for poly in polygons:
        size = len(poly)
        for i in range(size + 1):
            a = poly[i % size]
            b = poly[(i + 1) % size]
            graph[a].add(b)
            graph[b].add(a)

    return graph


def merge_corners_onto_borders(graph):
    """
    Find the places where corners intersect a border line segment, and merge
    them into the graph at that point.
    """
    # Iterate over the border line segments, and find which grid points each
    # one passes through.
    points = set(graph.keys())
    edges = graph_edges(graph)
    while edges:
        a, b = edges.pop()
        for p in segment_lattice_points(a, b):
            if p in points:
                # We have found a corner that is exactly on a border. Split the
                # border line and add in the new corner.
                graph[a].remove(b)
                graph[b].remove(a)
                edges.add(tuple(sorted((a, p))))
                graph[a].add(p)
                graph[p].add(a)
                edges.add(tuple(sorted((b, p))))
                graph[b].add(p)
                graph[p].add(b)
                break


def graph_edges(graph):
    """
    Find the unique edges of a graph.
    """
    edges = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            # Canonicalize the edge.
            edges.add(tuple(sorted((node, neighbor))))
    return edges


def segment_lattice_points(a, b):
    """
    Find all integer lattice points which intersect the given line segment.
    """
    step_x, step_y = fraction_slope(a, b)

    # Iterate over points on the segment, excluding the start and end points.
    points = []
    ax, ay = a
    bx, by = b
    x = ax + step_x
    y = ay + step_y
    while x != bx or y != by:
        points.append((x, y))
        x += step_x
        y += step_y

    return points


def fraction_slope(a, b):
    """
    Find the slope of the line segment as a lowest-terms fraction.
    """
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    divisor = gcd(dx, dy)
    return (
        dx // divisor,
        dy // divisor,
    )


def gcd(a, b):
    """
    Euclid's algorithm to find the greatest common denominator.

    >>> gcd(12, 21)
    3
    >>> gcd(53473753604, 32407556409)
    271
    """
    while b != 0:
        temp = a % b
        a = b
        b = temp
    return a


def continue_straight_lines(graph):
    """
    Find multiple edges creating a continuous straight line.
    Make them "skip" over connections to create uninterrupted edges.
    """
    # For each node, find local continuations.
    for node in list(graph.keys()):
        neighbors = list(graph[node])

        # Find slopes of connected edges.
        slopes = []
        for neighbor in neighbors:
            slopes.append(fraction_slope(node, neighbor))

        # Check all pairs for matching slopes.
        for left_index in range(len(slopes)):
            for right_index in range(left_index + 1, len(slopes)):
                if (
                    slopes[left_index][0] == slopes[right_index][0] and
                    slopes[left_index][1] == slopes[right_index][1]
                ):
                    # We have a match, so connect across this node.
                    left = neighbors[left_index]
                    right = neighbors[right_index]

                    graph[node].remove(left)
                    graph[left].remove(node)
                    graph[node].remove(right)
                    graph[right].remove(node)
                    graph[left].add(right)
                    graph[right].add(left)
