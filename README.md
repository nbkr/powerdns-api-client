# powerdns-api-client

Quick and Dirty API Client for my DNS setup. See: https://benjaminfleckenstein.name/the-overengineered-platform/dns.html for more details.

The script requires the following environment varibles to work:

* DNS_API_HOST_PREFIX \
    The hostname where PowerDNS runs. Usually something like https://dnsserver.example.com/
* DNS_API_PASS \
    The password for the HTTP-Auth-Challange of the reverse proxy. The username is currently hard coded to 'admin'.
* DNS_API_KEY \
    The API Passphrase set in the PowerDNS configuration.

The script expects the DNS data to be found in the 'data.yml' file.
