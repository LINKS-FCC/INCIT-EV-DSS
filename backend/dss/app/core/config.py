from pydantic import BaseSettings
import os
from OpenSSL import crypto

class Settings(BaseSettings):
    app_name: str = "INCIT-EV DSS"
    app_description: str = "INCIT-EV Decision Support System"
    version: str = "0.0.1"
    jwt_public_key = '-----BEGIN PUBLIC KEY----- MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwlEZLBXtkud6p3pY3Sn+ ly1O0PbcwRSapGGCXH6Iry/cURiuuG4gABH+84ddQk3uniFZOQcwDss9JQernQkV RlXGoYkhK2cWqdAJrXFIojbni14Z81JoyDh1ewvC4TpL0jAXUgmlBWZQZcLi65YF Hjvh6pjPcTPb+25tLpv803ZNq1i7bRZ3t4/kN2a0PTEBe+NJYRTDiusBu6uvdINi pqar9dVuAetJ4BddaOua6+2MQXh4PE/BaE/AtXCKJobJmhdWcnYU/2qqoTMZyiu9 qSmfivk2UCfeWB7eX/661gocnoWtYL4OQtGz2r3gC2AalrWEtLvFX5+Q0p2F/53/ h1VtsQw+kb2Mwk0P2KB4p++bm4DzoiJGqkyvYMO7T3Nu95U2s0peJkLD6HRCEFbt CzBfbv8oj7YzkZWEBijlbhwU28o2RdrCLKqR6M76//D6Q8fhox9cd+DapwyPPVxM fcsKWcaH1DbU39hRIQAjy6C8rQVTPtCukfSHudUKYewOEi6YJZA/c3cGGp3E4YfI S6fMNJEC57rhuUyG2RmJ3kUSZ1F62C2V6fW1d7BPbQwVmXdTtbhnu63Np33uS4oQ Nyn5ZpHMnXNDHJwbTazda8M8wtX94hH7AP1WsB7m7+E6YTh7GBcJGR4Qb41UkOdX IAlDsY9FL/r3s/75Xix8QI8CAwEAAQ== -----END PUBLIC KEY-----'
    jwt_private_key = '-----BEGIN RSA PRIVATE KEY----- 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 -----END RSA PRIVATE KEY-----'
    jwt_algorithm = "RS256"
    exp_min = 30
    mongo_uri = "mongodb://root:testing_db@localhost:27017/"
    db_name = "incitev"
    simulator_uri = "http://dss-integration:80/api/v1/simulations/"

settings = Settings()

if os.getenv("MONGO_USER") != None and os.getenv("MONGO_PASSWORD") != None:
    if os.getenv("MONGO_URI") != None:
        settings.mongo_uri = "mongodb://{}:{}@{}:27017/".format(os.getenv("MONGO_USER"), os.getenv("MONGO_PASSWORD"), os.getenv("MONGO_URI"))
    else:
        settings.mongo_uri = "mongodb://{}:{}@localhost:27017/".format(os.getenv("MONGO_USER"), os.getenv("MONGO_PASSWORD"))

if os.getenv("DATABASE_NAME") != None:
    settings.db_name = os.getenv("DATABASE_NAME")

if os.getenv("SIMULATOR_URI") != None:
    settings.simulator_uri = os.getenv("SIMULATOR_URI")

if os.getenv("DSS_PRIVATE_KEY") != None:
    with open(os.getenv("DSS_PRIVATE_KEY")) as fp:
        settings.jwt_private_key = fp.read()
        fp.close()

if os.getenv("DSS_PUBLIC_KEY") != None:
    with open(os.getenv("DSS_PUBLIC_KEY")) as fp:
        settings.jwt_public_key = fp.read()
        fp.close()

if os.getenv("DSS_CERTIFICATE") != None:
    with open(os.getenv("DSS_CERTIFICATE")) as fp:
        pub_obj = crypto.load_certificate(crypto.FILETYPE_PEM, fp.read()).get_pubkey()
        settings.jwt_public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, pub_obj).decode()
        fp.close()