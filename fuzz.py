import random
import canoepaddle
import vec
from district_borders import (
    polygons_to_graph,
    merge_corners_onto_borders,
    continue_straight_lines,
    graph_edges,
)


def rect_points(rect):
    left, bottom, width, height = rect
    points = set()
    for x in range(left, left + width):
        for y in range(bottom, bottom + height):
            points.add((x, y))
    return points


def gen_polygons():
    # Procedurally generate a lot of rectangular districts.
    num_districts = 1000
    min_size = 3
    max_size = 10
    max_ratio = 2.0

    def gen_rect():
        x = random.randrange(min_size, max_size + 1)
        ratio = random.uniform(1, max_ratio)
        y = int(round(x * ratio))
        if random.choice((True, False)):
            return x, y
        else:
            return y, x

    rectangles = []  # x, y, width, height
    occupied_points = set()

    districts_done = 0
    while districts_done < num_districts:
        width, height = gen_rect()

        if len(rectangles) == 0:
            rect = (0, 0, width, height)
            rectangles.append(rect)
            area = rect_points(rect)
            occupied_points.update(area)
            districts_done += 1
            continue

        base_x, base_y, base_width, base_height = random.choice(rectangles)
        x = base_x
        y = base_y

        if random.choice((True, False)):
            # Attach to left or right of base.
            if random.choice((True, False)):
                x += base_width  # Right side.
            else:
                x -= width  # Left side.
            if random.choice((True, False)):
                y += (base_height - height)  # Bottom align.
            else:
                pass  # Top align
        else:
            # Attach to top or bottom of base.
            if random.choice((True, False)):
                y += base_height  # Bottom side.
            else:
                y -= height  # Top side.
            if random.choice((True, False)):
                x += (base_width - width)  # Right align.
            else:
                pass  # Left align

        rect = (x, y, width, height)

        # Check collisions
        area = rect_points(rect)
        collide = any(p in occupied_points for p in area)
        if collide:
            continue
        occupied_points.update(area)
        rectangles.append(rect)
        districts_done += 1

    polygons = []
    for x, y, width, height in rectangles:
        polygons.append((
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ))

    return polygons


def draw_graph(graph):
    gap_size = 0.25

    p = canoepaddle.Pen()
    p.stroke_mode(0.1, 'black')
    for a, b in graph_edges(graph):
        gap = vec.norm(vec.vfrom(a, b), gap_size)
        p.move_to(vec.add(a, gap))
        p.line_to(vec.sub(b, gap))

    return p.paper


def draw_polygons(polygons):
    p = canoepaddle.Pen()
    p.fill_mode('#eee')
    for poly in polygons:
        p.move_to(poly[-1])
        for point in poly:
            p.line_to(point)
    return p.paper


if __name__ == '__main__':
    polygons = gen_polygons()

    graph = polygons_to_graph(polygons)
    merge_corners_onto_borders(graph)
    continue_straight_lines(graph)

    paper = canoepaddle.Paper()
    paper.merge(draw_polygons(polygons))
    paper.merge(draw_graph(graph))

    bounds = paper.bounds()
    bounds.left -= 2
    bounds.right += 2
    bounds.bottom -= 2
    bounds.top += 2
    paper.override_bounds(bounds)

    print(paper.format_svg(2))
