from typing import List
import cv2
import numpy as np


def projection_by_bboxes(boxes: np.array, axis: int) -> np.ndarray:
    """
     通过一组 bbox 获得投影直方图，最后以 per-pixel 形式输出

    Args:
        boxes: [N, 4]
        axis: 0-x坐标向水平方向投影， 1-y坐标向垂直方向投影

    Returns:
        1D 投影直方图，长度为投影方向坐标的最大值(我们不需要图片的实际边长，因为只是要找文本框的间隔)

    """
    assert axis in [0, 1]
    length = np.max(boxes[:, axis::2])
    res = np.zeros(length, dtype=int)
    # TODO: how to remove for loop?
    for start, end in boxes[:, axis::2]:
        res[start:end] += 1
    return res


# from: https://dothinking.github.io/2021-06-19-%E9%80%92%E5%BD%92%E6%8A%95%E5%BD%B1%E5%88%86%E5%89%B2%E7%AE%97%E6%B3%95/#:~:text=%E9%80%92%E5%BD%92%E6%8A%95%E5%BD%B1%E5%88%86%E5%89%B2%EF%BC%88Recursive%20XY,%EF%BC%8C%E5%8F%AF%E4%BB%A5%E5%88%92%E5%88%86%E6%AE%B5%E8%90%BD%E3%80%81%E8%A1%8C%E3%80%82
def split_projection_profile(arr_values: np.array, min_value: float, min_gap: float):
    """Split projection profile:

    ```
                              ┌──┐
         arr_values           │  │       ┌─┐───
             ┌──┐             │  │       │ │ |
             │  │             │  │ ┌───┐ │ │min_value
             │  │<- min_gap ->│  │ │   │ │ │ |
         ────┴──┴─────────────┴──┴─┴───┴─┴─┴─┴───
         0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
    ```

    Args:
        arr_values (np.array): 1-d array representing the projection profile.
        min_value (float): Ignore the profile if `arr_value` is less than `min_value`.
        min_gap (float): Ignore the gap if less than this value.

    Returns:
        tuple: Start indexes and end indexes of split groups.
    """
    # all indexes with projection height exceeding the threshold
    arr_index = np.where(arr_values > min_value)[0]
    if not len(arr_index):
        return

    # find zero intervals between adjacent projections
    # |  |                    ||
    # ||||<- zero-interval -> |||||
    arr_diff = arr_index[1:] - arr_index[0:-1]
    arr_diff_index = np.where(arr_diff > min_gap)[0]
    arr_zero_intvl_start = arr_index[arr_diff_index]
    arr_zero_intvl_end = arr_index[arr_diff_index + 1]

    # convert to index of projection range:
    # the start index of zero interval is the end index of projection
    arr_start = np.insert(arr_zero_intvl_end, 0, arr_index[0])
    arr_end = np.append(arr_zero_intvl_start, arr_index[-1])
    arr_end += 1  # end index will be excluded as index slice

    return arr_start, arr_end


def recursive_xy_cut(boxes: np.ndarray, indices: List[int], res: List[int]):
    """

    Args:
        boxes: (N, 4)
        indices: 递归过程中始终表示 box 在原始数据中的索引
        res: 保存输出结果

    """
    # 向 y 轴投影
    assert len(boxes) == len(indices)

    _indices = boxes[:, 1].argsort()
    y_sorted_boxes = boxes[_indices]
    y_sorted_indices = indices[_indices]

    # debug_vis(y_sorted_boxes, y_sorted_indices)

    y_projection = projection_by_bboxes(boxes=y_sorted_boxes, axis=1)
    pos_y = split_projection_profile(y_projection, 0, 1)
    if not pos_y:
        return

    arr_y0, arr_y1 = pos_y
    for r0, r1 in zip(arr_y0, arr_y1):
        # [r0, r1] 表示按照水平切分，有 bbox 的区域，对这些区域会再进行垂直切分
        _indices = (r0 <= y_sorted_boxes[:, 1]) & (y_sorted_boxes[:, 1] < r1)

        y_sorted_boxes_chunk = y_sorted_boxes[_indices]
        y_sorted_indices_chunk = y_sorted_indices[_indices]

        _indices = y_sorted_boxes_chunk[:, 0].argsort()
        x_sorted_boxes_chunk = y_sorted_boxes_chunk[_indices]
        x_sorted_indices_chunk = y_sorted_indices_chunk[_indices]

        # 往 x 方向投影
        x_projection = projection_by_bboxes(boxes=x_sorted_boxes_chunk, axis=0)
        pos_x = split_projection_profile(x_projection, 0, 1)
        if not pos_x:
            continue

        arr_x0, arr_x1 = pos_x
        if len(arr_x0) == 1:
            # x 方向无法切分
            res.extend(x_sorted_indices_chunk)
            continue

        # x 方向上能分开，继续递归调用
        for c0, c1 in zip(arr_x0, arr_x1):
            _indices = (c0 <= x_sorted_boxes_chunk[:, 0]) & (
                x_sorted_boxes_chunk[:, 0] < c1
            )
            recursive_xy_cut(
                x_sorted_boxes_chunk[_indices], x_sorted_indices_chunk[_indices], res
            )
