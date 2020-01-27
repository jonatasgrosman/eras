import freeling_client as FC
from freeling_dicts import FreelingConstants_PT_BR as idiom

client = FC.FreelingClientForTagging('localhost',50005, idiom, 30)
res = client.msg2json('Eu gosto muito de chocolate.')
print(res)
