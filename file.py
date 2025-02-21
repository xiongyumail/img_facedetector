import os
import json
import shutil
import argparse


def process_images_based_on_scores(json_file_path, landmark_score=0.9, target_path='./copied_images', delete=False, copy=False):
    try:
        # 打开 JSON 文件并加载图像结果字典
        with open(json_file_path, 'r', encoding='utf-8') as f:
            image_result_dict = json.load(f)

        for file_path, results in image_result_dict.items():
            face_scores = results.get('face_scores', [])
            face_landmark_scores_68 = results.get('face_landmark_scores_68', [])

            # 计算人脸关键点分数的平均值
            if face_landmark_scores_68:
                avg_landmark_score = sum(face_landmark_scores_68) / len(face_landmark_scores_68)
            else:
                avg_landmark_score = 0

            # 处理删除操作
            if delete and (not face_scores or avg_landmark_score < landmark_score):
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted {file_path}")

            # 处理复制操作
            if copy and face_landmark_scores_68 and avg_landmark_score > landmark_score:
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                relative_path = os.path.relpath(file_path, os.path.dirname(json_file_path))
                target_dir = os.path.join(target_path, os.path.dirname(relative_path))
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                file_name = os.path.basename(file_path)
                shutil.copy2(file_path, os.path.join(target_dir, file_name))
                print(f"Copied {file_path} to {os.path.join(target_dir, file_name)}")

    except Exception as e:
        print(f"Error processing images: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images based on face landmark scores in a JSON file.')
    parser.add_argument('json_file_path', type=str, nargs='?', default='face.json',
                        help='Path to the JSON file containing face detection results. Default is face.json.')
    parser.add_argument('--landmark_score', type=float, default=0.9,
                        help='Threshold for face landmark scores.')
    parser.add_argument('--target_path', type=str, default='./copied_images',
                        help='Target path to copy the images. Default is./copied_images.')
    parser.add_argument('--delete', action='store_true', help='Delete images based on face scores and landmark scores.')
    parser.add_argument('--copy', action='store_true', help='Copy images based on face landmark scores.')

    args = parser.parse_args()

    # 检查是否至少指定了一个操作
    if not args.delete and not args.copy:
        print("Please specify at least one of --delete or --copy options.")
    else:
        process_images_based_on_scores(
            args.json_file_path,
            args.landmark_score,
            args.target_path,
            args.delete,
            args.copy
        )