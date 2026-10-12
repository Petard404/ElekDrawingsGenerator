"""Drawing dimensions with defaults and an optional override file."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Every dimension in mm. Fields are added as milestones need them.

    The layout values come from the measurements of House A page 1 (docs/layout-notes.md).
    Row offsets are measured from the row origin: the bus x, or the branch x of a branching circuit.
    """

    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    font_family: str = "Helvetica"
    default_stroke_mm: float = 0.25
    symbol_stroke_mm: float = 0.26

    # Frame and title block (House A page 1)
    frame_x: float = 0.5
    frame_y: float = 0.4
    frame_w: float = 209.2
    frame_h: float = 296.7
    frame_stroke_mm: float = 0.8
    title_x: float = 0.25
    title_w: float = 209.61
    title_bottom: float = 297.3
    title_row_h: float = 10.35
    title_split_x: float = 105.06
    title_stroke_mm: float = 0.5
    title_text_size: float = 4.23
    title_text_left: float = 3.9
    title_text_right: float = 108.9
    title_text_dy: float = 6.3      # baseline below the top of its row
    content_margin: float = 3.0     # content ends this far above the title block

    # Supply box
    supply_x: float = 5.7
    supply_y: float = 5.2
    supply_w: float = 25.3
    supply_h: float = 14.9
    supply_stroke_mm: float = 0.46
    supply_inner_x: float = 8.3
    supply_inner_y: float = 6.4
    supply_inner_w: float = 11.7
    supply_inner_h: float = 2.4
    supply_inner_stroke_mm: float = 0.38
    supply_voltage_x: float = 20.7
    supply_voltage_y: float = 8.4
    supply_voltage_size: float = 2.12
    supply_label_x: float = 8.1
    supply_label_y: float = 13.2
    supply_label_step: float = 4.4
    supply_label_size: float = 3.53
    supply_label_width: float = 22.9    # label wraps inside the box

    # Head levels: breakers and differentials in a chain from the supply, drawn from head_x
    head_x: float = 13.4
    head_first_level_y: float = 31.05
    head_level_spacing: float = 26.05
    head_loop_x: float = 32.94      # return loop between levels, absolute x
    head_loop_drop: float = 12.56
    head_text_dx: float = 4.7       # differential texts, from the level origin
    head_text_dy: float = 6.8       # first baseline below the line
    head_text_step: float = 3.6
    group_x: float = 42.4           # origin of the differentials that follow the last level
    feeder_x: float = 34.57         # vertical feeder to the second and later group children

    # Grid
    first_row_y: float = 57.43
    row_pitch: float = 15.35
    bus_x: float = 63.53
    wire_stroke_mm: float = 0.2

    # Breaker, rating and cable text, conductors mark
    breaker_start_dx: float = 3.3   # terminal a of the breaker symbol
    breaker_end_dx: float = 13.3    # terminal b; the line resumes here
    rating_dx: float = 3.2
    rating_dy: float = -5.65
    cable_dx: float = 14.4
    cable_dy: float = 2.3
    conductors_dx: float = 18.5     # centre of the conductors mark
    conductors_count_dx: float = 1.8   # count text, from the centre of the mark
    conductors_count_dy: float = -0.8

    # Nested breaker: breaker from the bus, loop to the right and back, bus continues below
    loop_dx: float = 19.64          # loop wire, from the bus
    loop_drop: float = 12.56
    nested_label_dx: float = 0.0    # label below the breaker, from the bus
    nested_label_dy: float = 7.4
    nested_cable_dx: float = 5.0    # cable text under the return line
    nested_cable_dy: float = 2.33
    nested_conductors_dx: float = 14.0  # centre of the conductors mark on the return line
    nested_child_lines: int = 2     # grid lines from the breaker row to its first child row

    # Device slots
    first_stem_dx: float = 34.76
    device_pitch: float = 7.66
    device_drop: float = 3.9        # stem from the line to the device, and between stacked devices
    id_dy: float = 9.0              # ID baseline below the line
    id_gap: float = 3.3             # ID baseline below the lowest symbol of a slot with stacked symbols
    count_dx: float = 0.6           # count and note without a label point on the symbol
    count_dy: float = 3.6

    # Circuit letter and description
    description_x: float = 160.95
    description_line_step: float = 3.6
    description_width: float = 46.0
    device_margin: float = 2.0      # the last device must end this far left of description_x

    # Text sizes
    text_size: float = 2.88         # rating, circuit letter, description
    small_text_size: float = 1.8    # cable text, IDs
    count_text_size: float = 1.73   # counts and notes
