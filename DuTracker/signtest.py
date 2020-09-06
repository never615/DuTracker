#!/usr/bin/env python
# @Time    : 2020/9/6 7:40 下午
# @Author  : never615 <never615.com>
import execjs

# def get_sign_string(params: dict):
#     """
#         ::param {recommendId: "73", lastId: ""}
#     """
#     sign_string = ''
#     sort_params = {k: params[k] for k in sorted(params.keys())}
#     for k, v in sort_params.items():
#         sign_string += k + v
#     sign_string += "048a9c4943398714b356a696503d2d36"
#     # sign_string += "19bc545a393a25177083d4a748807cc0"
#     return sign_string
#
# si = get_sign_string({"spuId":"1013","productSourceName":"","propertyValueId":"0"})
# # sign = func(si)
# import hashlib
# m = hashlib.md5()
# m.update(si.encode("utf8"))
# sign = m.hexdigest()
# print(sign)


# {
# 	"sign": "d7abf7370225b75bf8827942e5b6854c",
# 	"spuId": "10903",
# 	"productSourceName": "",
# 	"propertyValueId": "0"
# }
spuId = '10903'
with open('sign/sign.js', 'r', encoding='utf-8') as f:
	all_ = f.read()
	ctx = execjs.compile(all_)
	sign = ctx.call('getSign',
									'productSourceNamepropertyValueId0spuId{}19bc545a393a25177083d4a748807cc0'.format(spuId))
									# 'spuId{}propertyValueId019bc545a393a25177083d4a748807cc0'.format(spuId))
									# 'spuId{}productSourceName19bc545a393a25177083d4a748807cc0'.format(spuId))
									# 'spuId{}19bc545a393a25177083d4a748807cc0'.format(spuId))
	print(sign)

# d7abf7370225b75bf8827942e5b6854c
# 51b27837395c09891665c0848f80f3cb

# 秘钥19bc545a393a25177083d4a748807cc0

# 拿brand接口做测试
# 签名结果 4ff93b98af1253fe192ff1328ed09081
# 参数 {"sign":"4ff93b98af1253fe192ff1328ed09081","catId":0}
# with open('sign/sign.js', 'r', encoding='utf-8') as f:
# 	all_ = f.read()
# 	ctx = execjs.compile(all_)
# 	sign = ctx.call('getSign',
# 									'catId019bc545a393a25177083d4a748807cc0')
# 	# 'spuId{}productSourceNamepropertyValueId019bc545a393a25177083d4a748807cc0'.format(spuId))
# 	print(sign)
