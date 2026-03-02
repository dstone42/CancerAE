from datetime import datetime
from io import BytesIO

from box_sdk_gen import (
    JWTConfig,
    BoxJWTAuth,
    BoxClient,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)

client_id = '59erkd9dbklry8897rzhuu6rgvc0efe6'
client_secret = 'Z8jq2NvSBQcx7gnha7ssGsKj8S4RjmUS'
key_id = '8hmm4h82'
private_key = '-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIIFHDBOBgkqhkiG9w0BBQ0wQTApBgkqhkiG9w0BBQwwHAQI3MlAI3w9cBMCAggA\nMAwGCCqGSIb3DQIJBQAwFAYIKoZIhvcNAwcECM7yExSyVPt5BIIEyNNWW72tMa80\n/PpnAg49wv6rw9HHstkk0ZVeTEA1YoQZB7Kl3nCWwN5TJvdYeGl9kUwerxktedOg\nMWeF4mZ+TKIdOI5boNCuNZb9Aq412WjhZckIXtAbrrRh26e6QhSV4pujuy3I+rlt\nA0Eg4oq3oRGLpZ/a/Fm8IyBbNm7ngrnFJIY2+foPA8k/WvurR5EF9jBEIqY6vLcP\nfDp/bQL2hyoFV5ygA/S6A95eS8ipCswnb77O3LBQ9DNQyckh9cbHkpUi9UoDGVQp\nXf5yAScTP4X6f42mU6+37RR49u48Xnom4r7HuZJne5fdNYQ7OFLEz3gV637+qRho\naHSB0GdNBAYLGon/SKsw4gNvejQvpMw2jTrkO9QLIzeg3f3sqL+adfZlcnKVcUjI\nbhkh3pdY/RX93CzGOIAmuCy7fRCJefWQoDIr01z0TE+FQFTHCLhpVllugYEHJkt0\ncnWEJwk3v9tkJKDKRvNLD3FJTMAlkhoZQDDghx32QR3/vkSjj/aSu7LcX8zj9UrX\n2/B7f7UbihEw9UTxx1PIthol8S+k+XyRD2egcphSiEmJenf3nFSLtcZSDr5FSl3h\n0z9ZQAQ+sxqRy8cPKSzw/vZPcgxADPO2Iak9WCz2MVYbp5JU+dFMHt499qBxQqw6\nLFXWsjpsnYY3FktJvMdVl6VPF4sUaBa1mR/gbOtIjhyPL4Wj/yC4bQ7i0J+DRxgg\njSC2HJ4Kjifg5kVwxuH89aL4Fylbp9uNuGg0VBYjuDkXNkCjoFBHaQhz3P/FFFxr\n9XMkC+W9WFqIsI0GIsTKc7aZWEDfykWodsVCGFAZyrZkFvlh7Fwol0dUtfp37GaB\nkNzcU0JOvCncC1IhHn+8PNFtN8J/xZAJJ3Ku6DQwQpNQlBn+VaCHMIEHeEDOYVEP\nFLsEBdFa43E6c/VkVGiqMllpbgN7I36RttN4LgV61CXqbDZaztPiIkIoLjT8/O+b\nJMl1W+1bGE3BiCN3ZxEVlqAud7dP/+oB40I4MdtpmWYdYUMOIOi8dH8pJrM7ADts\nNXdJgfzj8rV1tKQdexWee8f0CH2RzPfqUsWL5kxNa3HO3m0jO3tRRC1mLfOeh196\nXG+ToZx8GXxfql0scO7TA803RMeTIXXgxNbGC+osbtfx1c45yj4WGvJPvoAi49mw\n0jsbeIMQUuFk7XAjq8h9NzgdSP4y8SNvllJFcts2rb60z0xYfnCRAsgkMimnNN7J\ny6IM+i+/eEqMkjlr/qUJ9XiQS7KMtTy25qdqMQBFDEdZ7RlTBhnIyw5x7xE2Gb+I\nLkI1IfRVm4GmsPDJXg9CwaSW+H/xC+OQQTrds9tWHu/XLcXY/CPOrG0A56SnIxLC\niT3NC7Ha/rad1MxpfmkwOtTPBcLCR/vwwk3RPjMkQCBcUyI403BC4ihkdZMcrXkq\nIuZPG2ptvZTHHmLn0d5iMpgHl/I4V9YPv6uU5JYSlR0JuMDQy5zM5T4XeKs2E09V\nBgBsz96z93lReUnJBdUfiSRLnXr3GmcXBUmYhW3oy52Qsj+KsMX9+3rOWxzpUb2s\nRADCIsemJ94DDPSzroVZHk/blEqj56irxerPTEXyFjqA3/HRY41yd8avyueL/sMR\nsjErl0D11BHS9Ut7V8grQg==\n-----END ENCRYPTED PRIVATE KEY-----\n'
passphrase = '4b7db3d1ce3a51721d9851aa4c5c0dc1'
enterprise_id = '223716'

config: JWTConfig = JWTConfig(client_id=client_id, client_secret=client_secret, jwt_key_id=key_id, private_key=private_key, private_key_passphrase=passphrase, enterprise_id=enterprise_id)
auth: BoxJWTAuth = BoxJWTAuth(config=config)
client: BoxClient = BoxClient(auth=auth)

# Upload test: writes a tiny text file to Box root folder (id "0")
box_parent_folder_id = "0"
test_name = f"box_write_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
payload = f"Box upload test at {datetime.utcnow().isoformat()}Z\n".encode("utf-8")
content_stream = BytesIO(payload)

upload_result = client.uploads.upload_file(
    UploadFileAttributes(
        name=test_name,
        parent=UploadFileAttributesParentField(id=box_parent_folder_id),
    ),
    content_stream,
)

uploaded = upload_result.entries[0]
print(f"Uploaded file successfully: id={uploaded.id}, name={uploaded.name}")