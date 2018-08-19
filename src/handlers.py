"""
    Collection of messages handler for different messages types.
"""
import hashlib
import io
from PIL import Image
import imagehash
import src.database as db

def normalize_url(url):
    if url[-1] == '/':
        url = url[:-1]
    if not url.startswith('https'):
        url = url.replace('http', 'https')
    if not url.startswith('https'):
        url = 'https://' + url
    url = url.lower()
    return url


def hash(*args):
    """
        Get the result hex digest of SHA256 applied to the passed strings.
    """
    m = hashlib.sha256()
    for arg in args:
        if isinstance(arg, bytes) or isinstance(arg, bytearray):
            m.update(arg)
        elif isinstance(arg, str):
            m.update(bytes(arg, 'utf-8'))
        else:
            m.update(bytes(str(arg), 'utf-8'))
    return m.hexdigest()


def hash_photo(update):
    res = []
    for photo in update.message.photo:
        h = str(imagehash.average_hash(
            Image.open(
                io.BytesIO(photo.get_file().download_as_bytearray())
            ),
            hash_size=8
        ))
        if not h in res:
            res.append(h)
    return res


def check_hash(update, h):
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    if isinstance(h, list):
        # check every hash in the list but alert once
        original_id = None
        for entity_hash in h:
            id = db.get_or_insert(chat_id, entity_hash, message_id)
            if not original_id:
                original_id = id
    else:
        original_id = db.get_or_insert(chat_id, h, message_id)

    if original_id:
        update.message.reply_text(
            'You probably reposted this :)',
            reply_to_message_id=original_id
        )


def photo_handler(bot, update):
    check_hash(update, hash_photo(update))


def forwarded_handler(bot, update):
    if update.message.forward_from:
        from_id = update.message.forward_from.id
    else:
        from_id = update.message.forward_from_chat.id

    if update.message.photo:
        check_hash(update, hash_photo(update))
    else:
        text = update.message.text
        digest = hash(from_id, text)
        check_hash(update, digest)


def url_handler(bot, update):
    """
        Got an url, check if there are links and store them. Or alert if the
        link was already seen in the same chat.
    """
    entities = update.message.parse_entities(types='url')
    for k in entities:
        url = normalize_url(entities[k])
        check_hash(update, hash(url))


def text_link_handler(bot, update):
    """
        Got a text link, check if there are links and store them. Or alert if
        the link was already seen in the same chat.
    """
    for entity in update.message.entities:
        if entity.url:
            url = normalize_url(entity.url)
            check_hash(update, hash(url))
