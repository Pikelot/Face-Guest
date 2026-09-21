$ORIGIN faceguest.com.
$TTL 300

@   IN  SOA ns.faceguest.com. admin.faceguest.com. (
        2026012201
        3600
        1800
        1209600
        300
)

@   IN  NS  ns.faceguest.com.
ns  IN  A   192.168.0.13
@   IN  A   192.168.0.13
db  IN  A   192.168.0.13
www IN  A   192.168.0.13