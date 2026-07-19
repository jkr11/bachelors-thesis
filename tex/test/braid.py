def generate_braid_tikz(num_strands, crossings):
  """
  - num_strands (int): Total number of strands
  - crossings (list of tuples): list (position, over_under)
  """
  dx = 0.8
  dy = 1.5

  current_positions = {i: (i - (num_strands + 1) / 2) * dx for i in range(1, num_strands + 1)}

  lines = []
  lines.append(r"\begin{tikzpicture}[yscale=1.0]")

  for i in range(1, num_strands + 1):
    x = current_positions[i]
    lines.append(f"  \\draw ({x:.2f}, 0.3) node {{\\color{{blue}}\\scalebox{{.6}}{{{i}}}}};")

  current_y = 0.0

  for _, (p, direction) in enumerate(crossings):
    next_y = current_y - dy

    x_left = (p - (num_strands + 1) / 2) * dx
    x_right = ((p + 1) - (num_strands + 1) / 2) * dx

    for i in range(1, num_strands + 1):
      track_x = (i - (num_strands + 1) / 2) * dx
      if track_x != x_left and track_x != x_right:
        lines.append(f"  \\draw[line width=1.4] ({track_x:.2f}, {current_y:.2f}) to ({track_x:.2f}, {next_y:.2f});")

    if direction == 1:
      under_start, under_end = x_right, x_left
      over_start, over_end = x_left, x_right
    else:
      under_start, under_end = x_left, x_right
      over_start, over_end = x_right, x_left

    lines.append(
      f"  \\draw[line width=1.4] ({under_start:.2f}, {current_y:.2f}) .. controls ({under_start:.2f}, {current_y - dy / 2:.2f}) and ({under_end:.2f}, {current_y - dy / 2:.2f}) .. ({under_end:.2f}, {next_y:.2f});"
    )

    lines.append(
      f"  \\draw[line width=4.5, white] ({over_start:.2f}, {current_y:.2f}) .. controls ({over_start:.2f}, {current_y - dy / 2:.2f}) and ({over_end:.2f}, {current_y - dy / 2:.2f}) .. ({over_end:.2f}, {next_y:.2f});"
    )

    lines.append(
      f"  \\draw[line width=1.4] ({over_start:.2f}, {current_y:.2f}) .. controls ({over_start:.2f}, {current_y - dy / 2:.2f}) and ({over_end:.2f}, {current_y - dy / 2:.2f}) .. ({over_end:.2f}, {next_y:.2f});"
    )

    current_y = next_y

  lines.append(r"\end{tikzpicture}")
  return "\n".join(lines)


if __name__ == "__main__":
  strands = 6

  sequence = [(3, 1), (2, -1), (4, 1), (3, -1), (1, 1), (5, -1)]

  tikz_code = generate_braid_tikz(strands, sequence)
  print(tikz_code)
