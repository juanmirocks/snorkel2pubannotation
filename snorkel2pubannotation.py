import json
import copy

_TEMPLATE = {
    "target": None,  # e.g. http://pubannotation.org/docs/sourcedb/PubMed/sourceid/10089213
    "sourcedb": None,
    "sourceid": None,
    "text": None,
    "project": None,
    "denotations": [],
    "relations": []
}

_COLUMN_SEPARATION = '\t'

def set_provenance(ret, id_type, doc_id):
    if id_type == "PMID":
        sourcedb = "PubMed"
    # else, PMC

    ret["target"] = "http://pubannotation.org/docs/sourcedb/{}/sourceid/{}".format(sourcedb, doc_id)
    ret["sourcedb"] = sourcedb
    ret["sourceid"] = doc_id

    return ret


def convert(text_file_path, denotations_file_path, relations_file_path):
    ret = copy.deepcopy(_TEMPLATE)

    with open(text_file_path) as fn:
        header = next(fn)
        id_type, _ = header.split(_COLUMN_SEPARATION)
        assert id_type == "PMID", "Current support only for PMID's (PubMed)"

        line = next(fn)
        doc_id, text = line.split(_COLUMN_SEPARATION)
        ret = set_provenance(ret, id_type, doc_id)

        text = text.strip()
        text = text[1:-1]
        text = text.replace("\\n", "\n")

        ret["text"] = text

    with open(denotations_file_path) as fn:
        next(fn)  # skip header

        for line in fn:
            did, prefix, eid, begin, end = line.split(_COLUMN_SEPARATION)

            d = {
                "id": did,
                    "span": {
                        "begin": int(begin),
                        "end": int(end)
                        },
                "obj": prefix + ":" + eid
            }

            ret["denotations"].append(d)

    with open(relations_file_path) as fn:
        next(fn)  # skip header
        pred = "linked"
        rel_count = 0

        for line in fn:
            _, _, d1_id, d2_id = line.split(_COLUMN_SEPARATION)

            r = {
                "id": "R"+str(rel_count),
                "pred": pred,
                "subj": d1_id.strip(),
                "obj": d2_id.strip()
            }

            ret["relations"].append(r)

            rel_count += 1

    ret = json.dumps(ret)

    return ret

if __name__ == '__main__':
    import sys
    text_file_path = sys.argv[1]
    denotations_file_path = sys.argv[2]
    relations_file_path = sys.argv[3]

    ret = convert(text_file_path, denotations_file_path, relations_file_path)
    print(ret)
