# coding=utf-8

import module.util.freeling.freeling_server as FS
import re



class FreelingClientForTagging(object):
    @FS.check_server('Server not ready')
    def __init__(self, host, port, timeout=15.0):

        self.s = FS.FreeLingClient(host, port, 'utf-8', timeout)

    def regexp_filter(self, str_to_change, regexp_dict):

        for case in regexp_dict:
            str_to_change = re.sub(case, regexp_dict[case], str_to_change)

        return str_to_change

    def msg2json(self, msg, dict_filter={}):

        if dict_filter and len(dict_filter) != 0:
            msg = self.regexp_filter(msg, dict_filter)

        # freeling postagger
        result = self.s.process(msg)

        # result
        result = result.split("\n")
        final_list = []
        [final_list.append(line.split(" ")) for line in result]

        final_list = final_list[0:(len(final_list) - 1)]  # deleting the last '' in list, marking the end of msg

        # JSON parsing
        msg_json = []
        msg_sentence = []
        for t in final_list:
            if t[0] == '':
                msg_json.append({"tokens": msg_sentence})
                msg_sentence = []
            else:
                msg_sentence.append({"FORM": t[0], "LEMMA": t[1], "POS": t[2], "PROB": float(t[3])})

        msg_json = {"sentences": msg_json}

        return msg_json
