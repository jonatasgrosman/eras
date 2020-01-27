import time
from module import config
from module.service.serviceException import ServiceException
from module.util.freeling.freeling_client import FreelingClientForTagging


def tokenizer_postagger(text, lang, dict_filter, smart_sentence_segmentation=False, smart_word_segmentation=False):

    freeling_type = 'default' if not smart_word_segmentation else 'with-smart-word-segmentation'

    client = FreelingClientForTagging(config['FREELING_HOST'][lang], config['FREELING_PORT'][lang][freeling_type])

    if smart_sentence_segmentation:
        return client.msg2json(text, dict_filter)
    else:

        document = {'sentences': []}

        for line in text.splitlines():

            if line:

                result = client.msg2json(line, dict_filter)

                line_sentence = {'tokens': []}
                for sentence in result['sentences']:
                    line_sentence['tokens'] = line_sentence['tokens'] + sentence['tokens']

                document['sentences'].append(line_sentence)

        return document
