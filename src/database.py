import os
from pony.orm import *

from .stringutil import split_sentences, split_words


__db = Database()
set_sql_debug(True)


class Sentence(__db.Entity):
    sentence_text = Required(str, unique=True)
    words = Set(lambda: Word)


class Word(__db.Entity):
    word_text = Required(str, unique=True)
    sentences = Set(lambda: Sentence)


def init_db(filename):
    __db.bind(provider='sqlite', filename='%s/%s' % (os.getcwd(), filename), create_db=True)
    __db.generate_mapping(create_tables=True)


@db_session
def insert_line(line_str):
    """
    Inserts a line into the database.

    :param line_str: ``str``
    """
    sentences_list_str = split_sentences(line_str)
    for sentence_text in sentences_list_str:
        sentence_ent = __find_sentence_entity_or_create(sentence_text)
        for word_text in split_words(sentence_text):
            word_ent = __find_word_entity_or_create(word_text)
            sentence_ent.words.add(word_ent)
            word_ent.sentences.add(sentence_ent)


@db_session
def insert_bulk(lines):
    for line in lines:
        insert_line(line)


@db_session
def is_word_known(word_text):
    return Word.get(word_text=word_text) is not None


@db_session
def sentences_with_word(word_text, amount):
    if amount < 1:
        raise ValueError('amount cannot be less than 1')

    word_ent = Word.get(word_text=word_text)
    if word_ent is None:
        return []

    sentence_ent_list = Sentence.select(lambda s: word_ent in s.words).random(amount)[:amount]

    return [sentence_ent.sentence_text for sentence_ent in sentence_ent_list]

@db_session
def __find_sentence_entity_or_create(sentence_text):
    sentence_ent = Sentence.get(sentence_text=sentence_text)
    if sentence_ent is None:
        sentence_ent = Sentence(sentence_text=sentence_text, words=set())
    return sentence_ent


@db_session
def __find_word_entity_or_create(word_text):
    word_ent = Word.get(word_text=word_text)
    if word_ent is None:
        word_ent = Word(word_text=word_text, sentences=set())
    return word_ent