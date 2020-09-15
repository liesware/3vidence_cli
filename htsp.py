import click
import json
import hashlib

import vars
import common
import htsp_curls

@click.group()
def htsp():
    pass

@htsp.command()
def curls():
    """API htsp curls
    """
    htsp_curls.api()

@htsp.command()
@click.argument('key_name')
def apikey_upd(key_name):
    """Update API KEY password
    """
    url=vars.eHost+'/htsp/apikey'
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not key_name in conf_data):
            print("Bad key name")
            return
        if (not "jwt" in conf_data):
            print("You need to login first")
            return
        message = {"api_key": conf_data[key_name]}
        headers={"Authorization":conf_data["jwt"]}
        response=common.sendingPut(url,message,headers)
        conf_data[key_name]= response["content"]["api_key"]
        with open(vars.fileConf, 'w') as outfile:
            json.dump(conf_data, outfile,indent=2)
        print("API updated OK!")


@htsp.command()
def health():
    """Health systems status
    """
    url=vars.eHost+'/htsp/health'
    response=common.sendingGet(url)
    print(json.dumps(response["content"],indent=2))

@htsp.command()
@click.argument('id_hjws')
def hjws(id_hjws):
    """Get a cloud id_hjws
    """
    url=vars.eHost+'/htsp/hjws/'+id_hjws
    response=common.sendingGet(url)
    print(json.dumps(response["content"],indent=2))

@htsp.command()
@click.argument('key_name')
@click.argument('id_hjws')
def hjws_del(key_name,id_hjws):
    """Delete a cloud id_hjws
    """
    url=vars.eHost+'/htsp/hjws'
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not key_name in conf_data):
            print("Bad key name")
            return
        message = {"api_key": conf_data[key_name], "id_hjws": id_hjws}
        response=common.sendingDel(url,message)
        print(json.dumps(response["content"],indent=2))

@htsp.command()
@click.argument('file_sign', type=click.File('r'))
@click.argument('key_name')
@click.option('-h','--hash', default="sha256", help='Hash algorithm ["sha224","sha256","sha384","sha512","whirlpool"]')
@click.option('-d','--desc', default="0545 cli", help='Description')
@click.option('-c','--cloud', default=True, help='Store signature on cloud [True/False]')
def htsq(file_sign,key_name,hash,desc,cloud):
    """Sign a file
    """
    url=vars.eHost+'/htsp/htsq'
    file_hash = common.hashCreate(hash,file_sign)
    if(file_hash==0):
        print("Bad algorithm")
        return
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not key_name in conf_data):
            print("Bad key name")
            return
        message = {"api_key": conf_data[key_name], "algorithm": hash,
            "hash":file_hash, "cloud": cloud,"desc": desc}
        response=common.sendingPost(url,message)
        if response["status_code"] != 200:
            print(json.dumps(response["content"],indent=2))
            return
        print(json.dumps(response["content"],indent=2))
        with open(file_sign.name+'.hjws', 'w') as outfile:
            json.dump(response["content"], outfile,indent=2)

@htsp.command()
@click.argument('file_sign', type=click.File('r'))
@click.option('-h','--hash', default="sha256", help='Hash algorithm ["sha224","sha256","sha384","sha512","whirlpool"]')
def htsq_anon(file_sign,hash):
    """Sign a file anonymously
    """
    url=vars.eHost+'/htsp/open/htsq'
    file_hash = common.hashCreate(hash,file_sign)
    if(file_hash==0):
        print("Bad algorithm")
        return
    message = {"algorithm": hash,"hash":file_hash}
    response=common.sendingPost(url,message)
    if response["status_code"] != 200:
        print(json.dumps(response["content"],indent=2))
        return
    print(json.dumps(response["content"],indent=2))
    with open(file_sign.name+'.hjws', 'w') as outfile:
        json.dump(response["content"], outfile,indent=2)

@htsp.command()
@click.argument('file_sign', type=click.File('r'))
def htsr(file_sign):
    """Verify a file with a hjws file
    """
    url=vars.eHost+'/htsp/htsr'
    with open(file_sign.name+'.hjws') as json_file:
        message = json.load(json_file)
        response=common.sendingPost(url, message)
        if response["status_code"] != 200:
            print(json.dumps(response["content"],indent=2))
            return
        file_hash = common.hashCreate(response["content"]["alg"],file_sign)
        if(file_hash==0):
            print("Bad algorithm")
            return
        if file_hash != response["content"]["hash"]:
            print("Bad file sign")
        else:
            print(json.dumps(response["content"],indent=2))

@htsp.command()
@click.argument('file_sign', type=click.File('r'))
@click.argument('id_hjws')
def htsr_cloud(file_sign,id_hjws):
    """Verify a file with a cloud id_hjws
    """
    url=vars.eHost+'/htsp/hjws/'+id_hjws
    response=common.sendingGet(url)
    if response["status_code"] != 200:
        print(json.dumps(response["content"],indent=2))
        return
    file_hash = common.hashCreate(response["content"]["alg"],file_sign)
    if(file_hash==0):
        print("Bad algorithm")
        return
    if file_hash != response["content"]["hash"]:
        print("Bad file sign")
    else:
        print(json.dumps(response["content"],indent=2))

@htsp.command()
def info():
    """Info account
    """
    url=vars.eHost+'/htsp/info'
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not "jwt" in conf_data):
            print("You need to login first")
            return
        headers={"Authorization":conf_data["jwt"]}
        response=common.sendingGet(url,headers)
        print(json.dumps(response["content"],indent=2))

@htsp.command()
def init():
    """Init account
    """
    url=vars.eHost+'/htsp/subject'
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        message = {"subject": conf_data["email"],"type":"email"}
        headers={"Authorization":conf_data["jwt"]}
        response=common.sendingPost(url,message,headers)
        if response["status_code"] != 200:
            print("Subject already exists")
            return
        conf_data["subject"]= response["content"]
        code = input("Your email verification code: ")
        url=vars.eHost+'/htsp/verification/'+code
        response=common.sendingGet(url,headers)
        if response["status_code"] != 200:
            print("Bad Verification code")
            return
        url=vars.eHost+'/htsp/branch'
        branch = input("Your branch name: ")
        message = {"id_sec": conf_data["subject"]["id_sec"],"branch":branch}
        headers={"Authorization":conf_data["jwt"]}
        response=common.sendingPost(url,message,headers)
        if response["status_code"] != 200:
            print(json.dumps(response["content"],indent=2))
            return
        conf_data[branch]= response["content"]["api_key"]
        with open(vars.fileConf, 'w') as outfile:
            json.dump(conf_data, outfile,indent=2)
        print("Init OK!")

@htsp.command()
@click.argument('key_name')
def info_apikey(key_name):
    """Info API key
    """
    url=vars.eHost+'/htsp/info/apikey'
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not key_name in conf_data):
            print("Bad key name")
            return
        message = {"api_key": conf_data[key_name]}
        response=common.sendingPost(url,message)
        print(json.dumps(response["content"],indent=2))

@htsp.command()
@click.argument('key_name')
def pubkey(key_name):
    """Info pub key
    """
    with open(vars.fileConf) as json_file:
        conf_data = json.load(json_file)
        if (not key_name in conf_data):
            print("Bad key name")
            return
        url=vars.eHost+'/htsp/pubkey/'+conf_data[key_name].split('.')[0]
        response=common.sendingGet(url)
        print(json.dumps(response["content"],indent=2))