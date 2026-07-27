def generate_braid_tikz(num_strands, sequence, dx=0.8, dy=1.5, gate_half_height=0.3, gate_pad=0.4):
  def strand_x(i):
    return (i - (num_strands + 1) / 2) * dx

  lines = []
  lines.append(r"\begin{tikzpicture}[yscale=1.0]")

  for i in range(1, num_strands + 1):
    x = strand_x(i)
    lines.append(f"  \\draw ({x:.2f}, 0.3) node {{\\color{{blue}}\\scalebox{{.6}}{{{i}}}}};")

  current_y = 0.0

  for entry in sequence:
    if len(entry) == 2:
      p, direction = entry
      kind, payload = "X", (p, direction)
    else:
      kind = entry[0]
      payload = entry[1:]

    next_y = current_y - dy
    mid_y = (current_y + next_y) / 2

    if kind == "X":
      p, direction = payload
      x_left = strand_x(p)
      x_right = strand_x(p + 1)

      for i in range(1, num_strands + 1):
        track_x = strand_x(i)
        if track_x != x_left and track_x != x_right:
          lines.append(f"  \\draw[line width=1.4] ({track_x:.2f}, {current_y:.2f}) to ({track_x:.2f}, {next_y:.2f});")

      if direction == 1:
        under_start, under_end = x_right, x_left
        over_start, over_end = x_left, x_right
      else:
        under_start, under_end = x_left, x_right
        over_start, over_end = x_right, x_left

      lines.append(
        f"  \\draw[line width=1.4] ({under_start:.2f}, {current_y:.2f}) "
        f".. controls ({under_start:.2f}, {current_y - dy / 2:.2f}) and "
        f"({under_end:.2f}, {current_y - dy / 2:.2f}) .. "
        f"({under_end:.2f}, {next_y:.2f});"
      )
      lines.append(
        f"  \\draw[line width=4.5, white] ({over_start:.2f}, {current_y:.2f}) "
        f".. controls ({over_start:.2f}, {current_y - dy / 2:.2f}) and "
        f"({over_end:.2f}, {current_y - dy / 2:.2f}) .. "
        f"({over_end:.2f}, {next_y:.2f});"
      )
      lines.append(
        f"  \\draw[line width=1.4] ({over_start:.2f}, {current_y:.2f}) "
        f".. controls ({over_start:.2f}, {current_y - dy / 2:.2f}) and "
        f"({over_end:.2f}, {current_y - dy / 2:.2f}) .. "
        f"({over_end:.2f}, {next_y:.2f});"
      )

    elif kind == "G":
      label, strands = payload
      strands = sorted(strands)
      xs = [strand_x(i) for i in strands]
      x_box_left = min(xs) - gate_pad
      x_box_right = max(xs) + gate_pad
      y_top = mid_y + gate_half_height
      y_bot = mid_y - gate_half_height

      for i in range(1, num_strands + 1):
        if i not in strands:
          track_x = strand_x(i)
          lines.append(f"  \\draw[line width=1.4] ({track_x:.2f}, {current_y:.2f}) to ({track_x:.2f}, {next_y:.2f});")

      for i in strands:
        x = strand_x(i)
        lines.append(f"  \\draw[line width=1.4] ({x:.2f}, {current_y:.2f}) to ({x:.2f}, {y_top:.2f});")

      lines.append(
        f"  \\filldraw[fill=white, draw=black, line width=1.2] ({x_box_left:.2f}, {y_top:.2f}) rectangle ({x_box_right:.2f}, {y_bot:.2f});"
      )
      lines.append(f"  \\node at ({(x_box_left + x_box_right) / 2:.2f}, {mid_y:.2f}) {{\\scriptsize {label}}};")

      for i in strands:
        x = strand_x(i)
        lines.append(f"  \\draw[line width=1.4] ({x:.2f}, {y_bot:.2f}) to ({x:.2f}, {next_y:.2f});")

    else:
      raise ValueError(f"Unknown sequence entry kind: {kind!r}")

    current_y = next_y

  lines.append(r"\end{tikzpicture}")
  return "\n".join(lines)


if __name__ == "__main__":
  strands = 6

  sequence = [
    (3, 1),
    (2, -1),
    ("G", "Injection", [3, 4, 5]),
    (4, 1),
    (3, -1),
    (1, 1),
    (5, -1),
  ]

  tikz_code = generate_braid_tikz(strands, sequence)
  print(tikz_code)
