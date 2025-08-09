import json
import os
import random


module_dir = os.path.dirname(__file__)
storage_path = os.path.join(module_dir, 'post storage.json')


def add_posts_to_next_batch(new_posts_list: list) -> None:
    """
    Appends a list of new posts to the 'next batch' section of the JSON storage.

    If the file or expected keys are missing, or if JSON is malformed,
    appropriate error is handled and no changes are made.

    :param new_posts_list: a list of posts (strings) to be added to 'next batch'.
    :return: None
    """
    try:
        with open(storage_path, 'r+', encoding='UTF-8') as f:

            try:
                batches_dict = json.load(f)
            except json.JSONDecodeError:
                print('"post storage.json" decode failure')
                return

            try:
                posts = batches_dict['next batch']
            except KeyError:
                print('"next batch" key is missing in "post storage.json"')
                return

            posts.extend(new_posts_list)

            try:
                f.seek(0)
                f.truncate()
                json.dump(batches_dict, f, ensure_ascii=False, indent=4)
            except TypeError:
                print('New posts batch serialization failure')

    except FileNotFoundError:
        print('"post storage.json" is not found')
    except OSError:
        print('OS can\'t open "post storage.json"')


def get_post_from_current_batch() -> str | None:
    """
    Randomly selects and removes one post from the 'current batch' section of the JSON storage.

    If the file or key is missing, JSON is malformed, or the batch is empty,
    appropriate error is handled and no changes are made.

    :return: a string post if available, or None if an error occurs or batch is empty.
    """
    post = None
    try:
        with open(storage_path, 'r+', encoding='UTF-8') as f:

            try:
                batches_dict = json.load(f)
            except json.JSONDecodeError:
                print('"post storage.json" decode failure')
                return None

            try:
                post_list = batches_dict['current batch']
                if not post_list:
                    print('"current batch" is empty')
                    return None

                random_index = random.randrange(len(post_list))
                post = post_list.pop(random_index)

                f.seek(0)
                f.truncate()
                json.dump(batches_dict, f, ensure_ascii=False, indent=4)
            except KeyError:
                print('"current batch" key is missing in "post storage.json"')
                return None

    except FileNotFoundError:
        print('"post storage.json" is not found')
    except OSError:
        print('OS can\'t open "post storage.json"')

    return post


def rotate_batches() -> int | None:
    """
    Moves all posts from 'next batch' section of JSON storage to 'current batch' and clears 'next batch'.

    Returns the number of posts in the updated 'current batch' after rotation.
    If the file or keys are missing, or JSON is malformed, appropriate error is handled and returns None.

    :return: Length of the updated 'current batch', or None if an error occurs.
    """
    current_batch_length = None

    try:
        with open(storage_path, 'r+', encoding='UTF-8') as f:

            try:
                batches_dict = json.load(f)
            except json.JSONDecodeError:
                print('"post storage.json" decode failure')
                return None

            try:
                old_posts_list = batches_dict['current batch']
            except KeyError:
                print('"current batch" key is missing in "post storage.json"')
                return None

            try:
                new_posts_list = batches_dict['next batch']
            except KeyError:
                print('"next batch" key is missing in "post storage.json"')
                return None

            old_posts_list.extend(new_posts_list)
            current_batch_length = len(old_posts_list)
            new_posts_list.clear()

            f.seek(0)
            f.truncate()
            json.dump(batches_dict, f, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        print('"post storage.json" is not found')
    except OSError:
        print('OS can\'t open "post storage.json"')

    return current_batch_length
