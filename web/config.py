
# CONFIG = {
#     "user": "2689562902@qq.com",
#     "password": "18796360983zs",
#     "host": "smtp.qq.com"
# }

MYSQL_CONFIG = {
    "user": "root",
    "password": "111111",
    "database": "user_info",
    "host": "47.106.83.33",
    "port": 3306
}

MongoDB_CONFIG = {
    "ip": "47.102.113.60",
    "port": "27017"
}


# 加密密钥: 项目一旦运行，不可修改 ==> 否则会造成老用户密码不匹配
SECRET_KEY = {
    #############################

    "KEY" : "this is Five五: p1BPjmRP+awXRTRI5B4T8Ye/XV4UEnbhC+rmADHUZWAIuAJo/h6oRhTP6OqG1LJ0pMuvSwJrga3k3daJuf2oR4MKl6O/QweolOsSF77D1A3PIS+aoZG9ywzXuwRB3md/648l6Qv+tZZ3ASet5r+Pmx7J1OadqA/EkcPP+w8/FMYnXe33/kAmzCsltICwDFyaNg8QsRTxNSsMZpMfI".encode(),
    "KEY2" : "3HE7JVBqnmW0UGX+L1xTXk7Vs7w8pwJ2H5723/Cq743+GQKAgOsr749rglsAOsltICwDFyaNg8QsRTxNSsMZpMfIpjXm4jaWOCqViqb//Ktw5avbOGPuRdKZjD1/4RaB+oZG0GDphky75q7wzyUQXmSmS+/o/NQiYzQK7WmfY71wv6BVKPLbHo0Vru4b+9Y0aSBNLA+IVIpiuQm3MYXFFSxz+ruqLoS5QvLhpbzCP329HKp4w1Zrv7XMSM86qO0UFN5P867xgW/ea5DGGbauBrUf3xBBWOwASo9UzrM28mheKuw1zp7vTkShKKTouwOFQrLZwo9gu1CqlPnTHme0dbWXaCzZYEo8bbG1qrn".encode()
    ####################################
}