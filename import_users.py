from models import User, ReferralProgram

file = open('../users.txt','r')

rp = ReferralProgram.objects().first()

import pdb
pdb.set_trace()
for line in file.readlines():
    dados = [x.strip() for x in line.split("|") if x.strip()]
    print("Saving {0} {1}".format(*dados))
    u = User()
    u.hash = dados[0]
    u.referral_program = rp
    u.user_indicator = None
    u.save()