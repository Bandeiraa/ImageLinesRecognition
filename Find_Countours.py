import pandas as pd
import numpy as np
import cv2
import math


def process_lines(image_src):
    img = image_src
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    thresh1 = cv2.bitwise_not(thresh1)

    edges = cv2.Canny(thresh1, threshold1=50, threshold2=200, apertureSize=3)

    lines = cv2.HoughLinesP(thresh1, rho=1, theta=np.pi / 180, threshold=50,
                            minLineLength=50, maxLineGap=30)

    # resizedImage = cv2.resize(img, (300, 300))
    # l[0] - line; l[1] - angle
    for line in get_lines(lines):
        leftx, boty, rightx, topy = line
        cv2.line(img, (leftx, boty), (rightx, topy), (0, 0, 255), 6)

    cdstP = np.copy(lines)

    # merge lines

    # ------------------
    # prepare
    _lines = []
    for _line in get_lines(lines):
        _lines.append([(_line[0], _line[1]), (_line[2], _line[3])])

    # sort
    _lines_x = []
    _lines_y = []
    for line_i in _lines:
        orientation_i = math.atan2((line_i[0][1] - line_i[1][1]), (line_i[0][0] - line_i[1][0]))
        if (abs(math.degrees(orientation_i)) > 45) and abs(math.degrees(orientation_i)) < (90 + 45):
            _lines_y.append(line_i)
        else:
            _lines_x.append(line_i)

    _lines_x = sorted(_lines_x, key=lambda _line: _line[0][0])
    _lines_y = sorted(_lines_y, key=lambda _line: _line[0][1])

    merged_lines_x = merge_lines_pipeline_2(_lines_x)
    merged_lines_y = merge_lines_pipeline_2(_lines_y)

    merged_lines_all = []
    merged_lines_all.extend(merged_lines_x)
    merged_lines_all.extend(merged_lines_y)
    # print("process groups lines", len(_lines), len(merged_lines_all))

    img_merged_lines = image_src
    blank_img = np.full(img_merged_lines.shape, 255, np.float32)
    for line in merged_lines_all:
        cv2.line(blank_img, (line[0][0], line[0][1]), (line[1][0], line[1][1]), (0, 0, 255), 6)

    imageResized = cv2.resize(img_merged_lines, (400, 400))
    cv2.imwrite('prediction/lines_gray.jpg', gray)
    cv2.imwrite('prediction/lines_thresh.jpg', thresh1)
    cv2.imwrite('prediction/lines_edges.jpg', edges)
    cv2.imwrite('prediction/lines_lines.jpg', img)
    cv2.imwrite('prediction/merged_lines.jpg', img_merged_lines)
    cv2.imwrite('prediction/whiteImage.jpg', blank_img)

    # cv2.imshow("Image", blank_img)

    return merged_lines_all


def merge_lines_pipeline_2(lines):
    super_lines_final = []
    super_lines = []
    min_distance_to_merge = 30
    min_angle_to_merge = 30

    for line in lines:
        create_new_group = True
        group_updated = False

        for group in super_lines:
            for line2 in group:
                if get_distance(line2, line) < min_distance_to_merge:
                    # check the angle between lines
                    orientation_i = math.atan2((line[0][1] - line[1][1]), (line[0][0] - line[1][0]))
                    orientation_j = math.atan2((line2[0][1] - line2[1][1]), (line2[0][0] - line2[1][0]))

                    if int(abs(
                            abs(math.degrees(orientation_i)) - abs(math.degrees(orientation_j)))) < min_angle_to_merge:
                        # print("angles", orientation_i, orientation_j)
                        # print(int(abs(orientation_i - orientation_j)))
                        group.append(line)

                        create_new_group = False
                        group_updated = True
                        break

            if group_updated:
                break

        if (create_new_group):
            new_group = []
            new_group.append(line)

            for idx, line2 in enumerate(lines):
                # check the distance between lines
                if get_distance(line2, line) < min_distance_to_merge:
                    # check the angle between lines
                    orientation_i = math.atan2((line[0][1] - line[1][1]), (line[0][0] - line[1][0]))
                    orientation_j = math.atan2((line2[0][1] - line2[1][1]), (line2[0][0] - line2[1][0]))

                    if int(abs(
                            abs(math.degrees(orientation_i)) - abs(math.degrees(orientation_j)))) < min_angle_to_merge:
                        # print("angles", orientation_i, orientation_j)
                        # print(int(abs(orientation_i - orientation_j)))

                        new_group.append(line2)

                        # remove line from lines list
                        # lines[idx] = False
            # append new group
            super_lines.append(new_group)

    for group in super_lines:
        super_lines_final.append(merge_lines_segments1(group))

    return super_lines_final


def merge_lines_segments1(lines, use_log=False):
    if (len(lines) == 1):
        return lines[0]

    line_i = lines[0]

    # orientation
    orientation_i = math.atan2((line_i[0][1] - line_i[1][1]), (line_i[0][0] - line_i[1][0]))

    points = []
    for line in lines:
        points.append(line[0])
        points.append(line[1])

    if (abs(math.degrees(orientation_i)) > 45) and abs(math.degrees(orientation_i)) < (90 + 45):

        # sort by y
        points = sorted(points, key=lambda point: point[1])

        if use_log:
            print("use y")
    else:

        # sort by x
        points = sorted(points, key=lambda point: point[0])

        if use_log:
            print("use x")

    return [points[0], points[len(points) - 1]]


def get_lines(lines_in):
    if cv2.__version__ < '3.0':
        return lines_in[0]
    return [l[0] for l in lines_in]


def lines_close(line1, line2):
    dist1 = math.hypot(line1[0][0] - line2[0][0], line1[0][0] - line2[0][1])
    dist2 = math.hypot(line1[0][2] - line2[0][0], line1[0][3] - line2[0][1])
    dist3 = math.hypot(line1[0][0] - line2[0][2], line1[0][0] - line2[0][3])
    dist4 = math.hypot(line1[0][2] - line2[0][2], line1[0][3] - line2[0][3])

    if (min(dist1, dist2, dist3, dist4) < 100):
        return True
    else:
        return False


def lineMagnitude(x1, y1, x2, y2):
    lineMagnitude = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
    return lineMagnitude


def DistancePointLine(px, py, x1, y1, x2, y2):
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
    LineMag = lineMagnitude(x1, y1, x2, y2)

    if LineMag < 0.00000001:
        DistancePointLine = 9999
        return DistancePointLine

    u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
    u = u1 / (LineMag * LineMag)

    if (u < 0.00001) or (u > 1):
        # // closest point does not fall within the line segment, take the shorter distance
        # // to an endpoint
        ix = lineMagnitude(px, py, x1, y1)
        iy = lineMagnitude(px, py, x2, y2)
        if ix > iy:
            DistancePointLine = iy
        else:
            DistancePointLine = ix
    else:
        # Intersecting point is on the line, use the formula
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        DistancePointLine = lineMagnitude(px, py, ix, iy)

    return DistancePointLine


def get_distance(line1, line2):
    dist1 = DistancePointLine(line1[0][0], line1[0][1],
                              line2[0][0], line2[0][1], line2[1][0], line2[1][1])
    dist2 = DistancePointLine(line1[1][0], line1[1][1],
                              line2[0][0], line2[0][1], line2[1][0], line2[1][1])
    dist3 = DistancePointLine(line2[0][0], line2[0][1],
                              line1[0][0], line1[0][1], line1[1][0], line1[1][1])
    dist4 = DistancePointLine(line2[1][0], line2[1][1],
                              line1[0][0], line1[0][1], line1[1][0], line1[1][1])
    return min(dist1, dist2, dist3, dist4)


def join_corners(df):
    max_value = df.max().max()

    new_df = df.copy()
    df_normalized = df / max_value

    distis = []
    threshold = 0.025
    for i, line in df_normalized.iterrows():
        for j, line2 in df_normalized[i + 1:].iterrows():
            if i != j:
                line1_p1 = (line[0], line[1])
                line1_p2 = (line[2], line[3])
                line2_p1 = (line2[0], line2[1])
                line2_p2 = (line2[2], line2[3])

                dist_1 = ((line1_p1[0] - line2_p1[0]) ** 2 + (line1_p1[1] - line2_p1[1]) ** 2) ** 0.5
                dist_2 = ((line1_p1[0] - line2_p2[0]) ** 2 + (line1_p1[1] - line2_p2[1]) ** 2) ** 0.5
                dist_3 = ((line1_p2[0] - line2_p1[0]) ** 2 + (line1_p2[1] - line2_p1[1]) ** 2) ** 0.5
                dist_4 = ((line1_p2[0] - line2_p2[0]) ** 2 + (line1_p2[1] - line2_p2[1]) ** 2) ** 0.5

                if threshold >= dist_1:
                    x_1, y_1 = new_df.loc[i][0: 2]
                    x_2, y_2 = new_df.loc[j][0: 2]

                    new_x = (x_1 + x_2) / 2
                    new_y = (y_1 + y_2) / 2

                    new_df.loc[i][0] = new_x
                    new_df.loc[i][1] = new_y
                    new_df.loc[j][0] = new_x
                    new_df.loc[j][1] = new_y
                elif threshold >= dist_2:
                    x_1, y_1 = new_df.loc[i][0: 2]
                    x_2, y_2 = new_df.loc[j][2: 5]

                    new_x = (x_1 + x_2) / 2
                    new_y = (y_1 + y_2) / 2

                    new_df.loc[i][0] = new_x
                    new_df.loc[i][1] = new_y
                    new_df.loc[j][2] = new_x
                    new_df.loc[j][3] = new_y
                elif threshold >= dist_3:
                    x_1, y_1 = new_df.loc[i][2: 5]
                    x_2, y_2 = new_df.loc[j][0: 2]

                    new_x = (x_1 + x_2) / 2
                    new_y = (y_1 + y_2) / 2

                    new_df.loc[i][2] = new_x
                    new_df.loc[i][3] = new_y
                    new_df.loc[j][0] = new_x
                    new_df.loc[j][1] = new_y
                elif threshold >= dist_4:
                    x_1, y_1 = new_df.loc[i][2: 5]
                    x_2, y_2 = new_df.loc[j][2: 5]

                    new_x = (x_1 + x_2) / 2
                    new_y = (y_1 + y_2) / 2

                    new_df.loc[i][2] = new_x
                    new_df.loc[i][3] = new_y
                    new_df.loc[j][2] = new_x
                    new_df.loc[j][3] = new_y

            distis.extend([dist_4, dist_3, dist_2, dist_1])

    return new_df


def generate_walls(path: str) -> dict:
    img = cv2.imread(path)
    tuple_data = process_lines(img)

    df = pd.DataFrame([(lst[0][0], lst[0][1], lst[1][0], lst[1][1]) for lst in tuple_data])
    df = join_corners(df)

    return df.to_dict(orient='split')
