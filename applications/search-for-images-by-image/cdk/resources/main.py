import os
from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import requests
import json
import time
import boto3
import multiprocessing
from elasticsearch import Elasticsearch, RequestsHttpConnection, exceptions
from requests_aws4auth import AWS4Auth
import urllib.request as urllib2
from urllib.parse import urlparse
import base64
from PIL import Image
from io import BytesIO

StagebaseURL=os.getenv("StagebaseURL","https://51wjfcue1d.execute-api.cn-north-1.amazonaws.com.cn/prod/")
bucket_name = os.getenv("bucket_name","ai-solution-kit-workshop-bucket43879c71-okavzifvpmzv")
# bucket_name = os.getenv("bucket_name","ask-workshop")
es_host = os.getenv("es_host","search-ask-workshop-q34k342llng4a54rk2bxaq5lwy.cn-north-1.es.amazonaws.com.cn")
region = os.getenv("region",'cn-north-1')
print(f"StagebaseURL:{StagebaseURL}")
print(f"bucket_name:{bucket_name}")
print(f"es_host:{es_host}")
print(f"region:{region}")

object_list = ["dress", "shoe", "handbag"]

k = 6
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
s3 = boto3.client('s3')

es = Elasticsearch(
    hosts = [{'host': es_host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)


def get_all_s3_keys(bucket):
    keys = []
    kwargs = {'Bucket': bucket}
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            if obj['Key'].endswith(".jpg"):
                keys.append('s3://' + bucket + '/' + obj['Key'])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
    return keys


def insert_index(s3_uri):
    payload = json.dumps({"url": s3_uri})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request("POST", StagebaseURL+"image-similarity/", headers=headers, data=payload)
        json_result = json.loads(response.text)
        type = s3_uri.split("/")[3]
        es.index(index='idx_ask',
                 body={"ask_img_vector": json_result["result"],
                       "image": s3_uri,
                       "type": type}
                )
    except:
        print("===================Request API Except==========")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
  return {"message": "AI Solution Kit workshop"}

@app.post("/create")
async def create():
    knn_index = {
        "settings": {
            "index.knn": True
        },
        "mappings": {
            "properties": {
                "ask_img_vector": {
                    "type": "knn_vector",
                    "dimension": 512,
                }
            }
        }
    }

    es.indices.create(index="idx_ask", body=knn_index, ignore=400)
    return {"message": "Create Index done!"}


@app.post("/init")
async def init():
    s3_uris = get_all_s3_keys(bucket_name)
    starttime = time.time()
    plimit = multiprocessing.cpu_count()
    print(f"plimit:{plimit}")
    parent_conns = []
    pcount = 0

    for s3_uri in s3_uris:
        # Create the pipe for parent-child process communication
        parent_conn, child_conn = multiprocessing.Pipe()
        # create the process, pass data to be operated on and connection
        process = multiprocessing.Process(target=insert_index, args=(s3_uri, ))
        parent_conns.append(parent_conn)
        process.start()
        pcount += 1

        if pcount == plimit:  # There is not currently room for another process
            # Wait until there are results in the Pipes
            finishedConns = multiprocessing.connection.wait(parent_conns)
            # Collect the results and remove the connection as processing
            # the connection again will lead to errors
            for conn in finishedConns:
                parent_conns.remove(conn)
                # Decrement pcount so we can add a new process
                pcount -= 1

    # Ensure all remaining active processes have their results collected
    for conn in parent_conns:
        conn.close()
    output = 'That took {} seconds'.format(time.time() - starttime)
    print(output)
    return {"message": "init index"}


@app.post("/delete")
async def delete():
    try:
        es.indices.delete(index="idx_ask")
        return {"message": "Deleted index"}
    except exceptions.NotFoundError:
        return {"message": "NotFound index"}


@app.get("/count")
async def count():
    index = es.count(index="idx_ask")
    return index


def extract_features(payload):
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", StagebaseURL+"image-similarity/", headers=headers, data=payload)
    json_result = json.loads(response.text)
    return json_result["result"]


def es_search(features,type = None):
    print(f'type:{type}')
    if type == None:
        body = {"size":k,'query': {'knn': {'ask_img_vector': {'vector': features, 'k': k}}}}
    else:
        body = {"size":k,
                'query': {
                    "bool":{
                        "must":[
                            {'knn': {'ask_img_vector': {'vector': features, 'k': 3*k}}},
                            {"term":{"type":type}},
                        ]}}}
    res = es.search(request_timeout=30, index="idx_ask",
                    body=body)
    return res


def presigned_url(s3_uri):
    index = s3_uri.find("/",5)
    current_bucket_name = s3_uri[5:index]
    key = s3_uri[index+1:]
    method_parameters = {'Bucket': current_bucket_name, 'Key': key}
    pre_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params=method_parameters,
        ExpiresIn=60
    )
    return pre_url


def do_search(payload, type = None):
    time_begin = time.time()
    features = extract_features(payload)
    time_features = time.time()
    print('features took {} seconds'.format(time_features - time_begin))
    res = es_search(features,type)
    time_search = time.time()
    print('search took {} seconds'.format(time_search - time_features))
    # print(len(res['hits']['hits']))
    result = []
    for i in range(len(res['hits']['hits'])):
        s3_uri = res['hits']['hits'][i]['_source']['image']
        pre_url = presigned_url(s3_uri)
        result.append(pre_url)
    return result


def find_objects(payload):
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", StagebaseURL+"object-recognition/", headers=headers, data=payload)
    json_result = json.loads(response.text)
    labels = json_result["Labels"]
    # for label in labels:
    #     if label["Name"] == "dress":
    #         box = label["Instances"][0]["BoundingBox"]
    #         return box
    for i in range(len(labels) - 1, -1, -1):
        if labels[i]["Name"] not in object_list:
            del labels[i]
    return labels


def readimg(payload_string):
    try:
        payload = json.loads(payload_string)
        if "url" in payload: # url形式
            value = payload["url"]
            if value.startswith('http'): # http url
                image = urllib2.urlopen(value).read()
            elif value.startswith('s3'): # s3 key
                o = urlparse(value)
                bucket = o.netloc
                path = o.path.lstrip('/')
                s3 = boto3.resource('s3')
                img_obj = s3.Object(bucket, path)
                image = img_obj.get()['Body'].read()
            else:
                raise
        elif "img" in payload: # base64形式
            value = payload["img"]
            image = base64.b64decode(value)
        else:
            raise
        return image
    except Exception as ex:
        print("出现如下异常%s"%ex)


def cut_img(image,box):
    img = Image.open(BytesIO(image))
    print(img.size)
    cropped = img.crop((int(img.size[0] * box["Left"]), int(img.size[1] * box["Top"]),
                        int(img.size[0] * (box["Left"] + box["Width"])),
                        int(img.size[1] * (box["Top"] + box["Height"]))))  # (left, upper, right, lower)
    print(cropped.size)
    buffered = BytesIO()
    cropped.save(buffered, format="JPEG")
    img_b64 = base64.b64encode(buffered.getvalue())
    return bytes.decode(img_b64)


def get_search_box(payload, box):
    # 读取原图
    image_string = readimg(payload)
    # 从原图中把对象切出来
    cut_img_b64 = cut_img(image_string, box)
    new_payload = {"img": cut_img_b64}
    return json.dumps(new_payload)


@app.post("/search")
async def search(body=Body(None)):
    payload = json.dumps(body)
    # print(f"payload:{payload}")
    # 找到对象坐标
    objects = find_objects(payload)
    # 如果没找到，全图搜索；如果只找到一个，直接搜索；如果大于1，则让用户选择
    if len(objects) > 1:
        return {"objects":objects,"list":[]}
    if len(objects) == 1:
        box = objects[0]["Instances"][0]["BoundingBox"]
        payload = get_search_box(payload,box)
    search_result = do_search(payload)
    return {"objects":objects,"list":search_result}


@app.post("/searchBox")
async def search_box(body=Body(None)):
    payload = json.dumps(body["payload"])
    box = body["box"]
    type = body["type"]
    payload = get_search_box(payload, box)
    search_result = do_search(payload,type)
    return {"objects":[],"list":search_result}

handler = Mangum(app)
# insert_index("s3://ai-solution-kit-workshop-bucket43879c71-okavzifvpmzv/shoe/my/1.jpg")